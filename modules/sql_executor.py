"""
SQL Executor - Executes SQL queries and extracts context from QGIS layers and databases
Supports: PostgreSQL/PostGIS, SpatiaLite, GeoPackage, Shapefiles
"""

from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsDataSourceUri,
    QgsMessageLog,
    Qgis,
    QgsFeature,
)
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from typing import Dict, List, Optional
import os


class SQLExecutor:
    """Executes SQL queries and extracts context from QGIS layers and databases."""

    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()
        self._db_credentials = None

    def _load_db_credentials(self) -> Dict:
        """Load database credentials from .env file"""
        if self._db_credentials is not None:
            return self._db_credentials

        self._db_credentials = {}
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        env_file = os.path.join(plugin_dir, ".env")

        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("#") and "=" in line:
                            key, value = line.strip().split("=", 1)
                            if key == "DB_HOST":
                                self._db_credentials["host"] = value
                            elif key == "DB_PORT":
                                self._db_credentials["port"] = value
                            elif key == "DB_NAME":
                                self._db_credentials["database"] = value
                            elif key == "DB_USER":
                                self._db_credentials["user"] = value
                            elif key == "DB_PASSWORD":
                                self._db_credentials["password"] = value
            except Exception as e:
                QgsMessageLog.logMessage(
                    f"Error loading DB credentials: {e}", "GeoAI Pro", Qgis.Warning
                )

        return self._db_credentials

    def get_context(self) -> Dict:
        """Collect detailed QGIS layer context for accurate SQL generation.
        If no layers are loaded, fetches table info directly from database.
        """

        project = QgsProject.instance()
        layers = project.mapLayers()

        context = {
            "layers": [],
            "tables": [],
            "table_fields": {},
            "db_type": "Unknown",
            "crs": project.crs().authid() if project.crs().isValid() else "Unknown",
            "selected_count": 0,
            "active_layer": (
                self.iface.activeLayer().name() if self.iface.activeLayer() else None
            ),
        }

        has_vector_layers = False
        for layer_id, layer in layers.items():
            if not isinstance(layer, QgsVectorLayer):
                continue

            has_vector_layers = True
            fields = [f.name() for f in layer.fields()]
            geom_field = self._detect_geom_column(layer)

            info = {
                "name": layer.name(),
                "provider": layer.providerType(),
                "geometry_field": geom_field,
                "geometry_type": layer.wkbType(),
                "feature_count": layer.featureCount(),
                "fields": fields,
            }

            # Detect database type
            source = layer.source().lower()
            if "postgresql" in source or "postgis" in source or "host=" in source:
                context["db_type"] = "PostgreSQL/PostGIS"
            elif "spatialite" in source:
                context["db_type"] = "SpatiaLite"
            elif "gpkg" in source:
                context["db_type"] = "GeoPackage"
            elif "shp" in source:
                context["db_type"] = "Shapefile"

            context["layers"].append(info)
            
            # For PostgreSQL layers, extract actual table name from source
            # For non-database layers (Shapefiles, etc.), don't add to tables list
            actual_table_name = None
            if "postgresql" in source or "postgis" in source or "host=" in source:
                try:
                    uri = QgsDataSourceUri(layer.source())
                    actual_table_name = uri.table()  # Get actual table name from PostgreSQL
                    schema = uri.schema() or "public"
                    if actual_table_name:
                        # Use schema.table format if schema is not public
                        if schema and schema != "public":
                            full_table_name = f"{schema}.{actual_table_name}"
                        else:
                            full_table_name = actual_table_name
                        context["tables"].append(full_table_name)
                        context["table_fields"][full_table_name] = fields
                        QgsMessageLog.logMessage(
                            f"PostgreSQL layer '{layer.name()}' maps to table '{full_table_name}'",
                            "GeoAI Pro",
                            Qgis.Info,
                        )
                    else:
                        # Fallback: use layer name if table extraction fails
                        context["tables"].append(layer.name())
                        context["table_fields"][layer.name()] = fields
                except Exception as e:
                    QgsMessageLog.logMessage(
                        f"Could not extract table name from layer '{layer.name()}': {e}. Using layer name.",
                        "GeoAI Pro",
                        Qgis.Warning,
                    )
                    context["tables"].append(layer.name())
                    context["table_fields"][layer.name()] = fields
            elif "spatialite" in source or "gpkg" in source:
                # For SpatiaLite/GeoPackage, try to extract table name
                try:
                    uri = QgsDataSourceUri(layer.source())
                    actual_table_name = uri.table()
                    if actual_table_name:
                        context["tables"].append(actual_table_name)
                        context["table_fields"][actual_table_name] = fields
                    else:
                        context["tables"].append(layer.name())
                        context["table_fields"][layer.name()] = fields
                except:
                    context["tables"].append(layer.name())
                    context["table_fields"][layer.name()] = fields
            # For Shapefiles and other file-based layers, don't add to tables
            # They are not database tables and shouldn't be queried with SQL

            # Count selections
            if layer.selectedFeatureCount() > 0:
                context["selected_count"] += layer.selectedFeatureCount()

        # Always try to fetch tables directly from database (prioritizes actual DB tables)
        db_context = self._get_database_tables_context()
        if db_context:
            # Merge database tables, but don't overwrite layer info
            for table_name, fields in db_context.get("table_fields", {}).items():
                if table_name not in context["table_fields"]:
                    context["table_fields"][table_name] = fields
                    if table_name not in context["tables"]:
                        context["tables"].append(table_name)
            # Update db_type if not set
            if context["db_type"] == "Unknown" and db_context.get("db_type"):
                context["db_type"] = db_context["db_type"]

        return context

    def _get_database_tables_context(self) -> Optional[Dict]:
        """Fetch table names and columns directly from PostgreSQL database."""
        env_creds = self._load_db_credentials()

        if not env_creds.get("database"):
            return None

        host = env_creds.get("host", "localhost")
        port = int(env_creds.get("port", 5432))
        database = env_creds.get("database", "")
        username = env_creds.get("user", "")
        password = env_creds.get("password", "")

        connection_name = f"GeoAI_Context_{database}"
        if QSqlDatabase.contains(connection_name):
            QSqlDatabase.removeDatabase(connection_name)

        db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        db.setHostName(host)
        db.setPort(port)
        db.setDatabaseName(database)
        db.setUserName(username)
        db.setPassword(password)

        if not db.open():
            QgsMessageLog.logMessage(
                f"Could not connect to database for context: {db.lastError().text()}",
                "GeoAI Pro",
                Qgis.Warning,
            )
            return None

        context = {
            "tables": [],
            "table_fields": {},
            "db_type": "PostgreSQL/PostGIS",
        }

        try:
            # Get all tables (excluding system tables)
            query = QSqlQuery(db)
            tables_sql = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type IN ('BASE TABLE', 'VIEW')
                AND table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys', 'raster_columns', 'raster_overviews')
                ORDER BY LOWER(table_name)
            """

            if query.exec_(tables_sql):
                while query.next():
                    table_name = query.value(0)  # Get exact case as stored in database
                    context["tables"].append(table_name)
                    QgsMessageLog.logMessage(
                        f"Found table: '{table_name}' (exact case from database)",
                        "GeoAI Pro",
                        Qgis.Info,
                    )

            # Get columns for each table
            for table_name in context["tables"]:
                # Use parameterized query to avoid SQL injection and handle case sensitivity
                columns_sql = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND LOWER(table_name) = LOWER(?)
                    ORDER BY ordinal_position
                """

                columns_query = QSqlQuery(db)
                columns_query.prepare(columns_sql)
                columns_query.addBindValue(table_name)
                
                if columns_query.exec_():
                    columns = []
                    while columns_query.next():
                        # Get the exact column name as stored in database (preserve case)
                        column_name = columns_query.value(0)
                        columns.append(column_name)
                    context["table_fields"][table_name] = columns
                    
                    QgsMessageLog.logMessage(
                        f"Fetched {len(columns)} columns for table '{table_name}': {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}",
                        "GeoAI Pro",
                        Qgis.Info,
                    )

            QgsMessageLog.logMessage(
                f"Fetched {len(context['tables'])} tables from database: {', '.join(context['tables'][:5])}{'...' if len(context['tables']) > 5 else ''}",
                "GeoAI Pro",
                Qgis.Info,
            )

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error fetching database context: {e}", "GeoAI Pro", Qgis.Warning
            )
        finally:
            db.close()
            QSqlDatabase.removeDatabase(connection_name)

        return context if context["tables"] else None

    def _detect_geom_column(self, layer: QgsVectorLayer) -> str:
        """Try to detect the geometry column name for PostGIS/SpatiaLite layers."""
        try:
            uri = QgsDataSourceUri(layer.source())
            geom = uri.geometryColumn()
            if geom:
                return geom
        except Exception:
            pass

        # Fallback for local datasets
        try:
            provider_fields = layer.dataProvider().fields()
            for f in provider_fields:
                if f.typeName().lower() in ["geometry", "geom"]:
                    return f.name()
        except Exception:
            pass

        return "geom"

    def execute_sql(self, sql: str, layer_name: Optional[str] = None) -> Dict:
        """Execute SQL query on specified layer or database."""

        try:
            # CRITICAL: Check .env for PostgreSQL credentials FIRST
            # If DB_NAME is set, ALWAYS use PostgreSQL (never SQLite)
            env_creds = self._load_db_credentials()
            force_postgres = bool(env_creds.get("database"))
            
            if force_postgres:
                QgsMessageLog.logMessage(
                    f"🔒 PostgreSQL mode: DB_NAME={env_creds.get('database')} found in .env - FORCING PostgreSQL execution",
                    "GeoAI Pro",
                    Qgis.Info
                )
            
            if layer_name:
                layers = self.project.mapLayersByName(layer_name)
                if not layers:
                    # If no layer but we have PostgreSQL credentials, use direct connection
                    if force_postgres:
                        return self._execute_direct_postgres(sql)
                    return {"error": f"Layer '{layer_name}' not found"}
                layer = layers[0]
            else:
                layer = self.iface.activeLayer()

            # If no layer, try direct database connection from .env
            if not layer:
                if force_postgres:
                    QgsMessageLog.logMessage(
                        "No layer selected, using direct PostgreSQL from .env",
                        "GeoAI Pro",
                        Qgis.Info
                    )
                return self._execute_direct_postgres(sql)

            provider_type = layer.dataProvider().name().lower()
            source = layer.source()
            source_lower = source.lower()
            
            # Log detection info for debugging
            QgsMessageLog.logMessage(
                f"SQL Executor - Provider: {provider_type}, Source: {source[:100]}...",
                "GeoAI Pro",
                Qgis.Info
            )

            # PRIORITY 1: Check PostgreSQL FIRST (most common for your use case)
            # Check multiple indicators of PostgreSQL connection
            is_postgres = False
            postgres_reason = ""
            
            # Method 1: Try parsing as PostgreSQL URI
            try:
                uri = QgsDataSourceUri(source)
                # If we can parse a host from URI, it's definitely PostgreSQL
                if uri.host():
                    is_postgres = True
                    postgres_reason = f"URI host detected: {uri.host()}"
                    QgsMessageLog.logMessage(
                        f"✅ Detected PostgreSQL via URI host: {uri.host()}, Database: {uri.database()}",
                        "GeoAI Pro",
                        Qgis.Info
                    )
            except Exception as e:
                QgsMessageLog.logMessage(
                    f"URI parsing failed: {str(e)}, trying other methods",
                    "GeoAI Pro",
                    Qgis.Warning
                )
            
            # Method 2: Check provider type (most reliable)
            if not is_postgres:
                if "postgres" in provider_type:
                    is_postgres = True
                    postgres_reason = f"Provider type: {provider_type}"
                    QgsMessageLog.logMessage(
                        f"✅ Detected PostgreSQL via provider type: {provider_type}",
                        "GeoAI Pro",
                        Qgis.Info
                    )
            
            # Method 3: Check source string for PostgreSQL indicators
            if not is_postgres:
                postgres_indicators = [
                    "postgres" in source_lower,
                    "postgis" in source_lower,
                    "host=" in source_lower,
                    "port=" in source_lower,
                    "dbname=" in source_lower,
                    "service=" in source_lower,  # PostgreSQL service file
                ]
                if any(postgres_indicators):
                    is_postgres = True
                    postgres_reason = "PostgreSQL indicators in source string"
                    QgsMessageLog.logMessage(
                        f"✅ Detected PostgreSQL via source string indicators",
                        "GeoAI Pro",
                        Qgis.Info
                    )
            
            # Method 4: If we have .env credentials and no layer connection, assume PostgreSQL
            if not is_postgres and not layer:
                env_creds = self._load_db_credentials()
                if env_creds.get("database"):
                    is_postgres = True
                    postgres_reason = "Using .env PostgreSQL credentials"
                    QgsMessageLog.logMessage(
                        f"✅ Using PostgreSQL from .env credentials",
                        "GeoAI Pro",
                        Qgis.Info
                    )
            
            if is_postgres:
                QgsMessageLog.logMessage(
                    f"🚀 Executing on PostgreSQL ({postgres_reason})",
                    "GeoAI Pro",
                    Qgis.Info
                )
                return self._execute_postgres(sql, layer)
            
            # PRIORITY 2: Check for file-based databases (SQLite/SpatiaLite/GeoPackage)
            # ONLY if PostgreSQL is NOT forced AND it's clearly a file path AND file exists
            is_file_db = False
            file_path = None
            
            # NEVER try SQLite if PostgreSQL is forced via .env
            if not force_postgres and provider_type in ["spatialite", "ogr"]:
                # Extract file path from source
                file_path = source.split("|")[0].split("?")[0].split("#")[0]
                # Check if it's actually a file path (not a connection string)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    # Check file extension to confirm it's a database file
                    if any(ext in file_path.lower() for ext in [".gpkg", ".sqlite", ".db", ".sqlite3"]):
                        is_file_db = True
                        QgsMessageLog.logMessage(
                            f"Detected file-based database: {file_path}",
                            "GeoAI Pro",
                            Qgis.Info
                        )
            
            if is_file_db and file_path and not force_postgres:
                return self._execute_spatialite(sql, layer)
            
            # If PostgreSQL is forced but we got here, use direct connection
            if force_postgres:
                QgsMessageLog.logMessage(
                    "PostgreSQL forced via .env, using direct connection",
                    "GeoAI Pro",
                    Qgis.Info
                )
                return self._execute_direct_postgres(sql)
            
            # PRIORITY 3: ALWAYS try direct PostgreSQL connection (from .env) if credentials exist
            # This ensures PostgreSQL is used when .env is configured
            env_creds = self._load_db_credentials()
            if env_creds.get("database"):
                QgsMessageLog.logMessage(
                    f"🚀 Using direct PostgreSQL connection from .env (Database: {env_creds.get('database')})",
                    "GeoAI Pro",
                    Qgis.Info
                )
                result = self._execute_direct_postgres(sql)
                # If connection succeeds OR if error is not about connection failure, return it
                if result.get("success") or ("error" in result and "connection failed" not in result.get("error", "").lower() and "does not exist" not in result.get("error", "").lower()):
                    return result
                # If database doesn't exist error, still return it (better than trying SQLite)
                if "does not exist" in result.get("error", ""):
                    return result
            
            # PRIORITY 4: Last resort - try attribute query for non-database layers
            QgsMessageLog.logMessage(
                f"PostgreSQL connection failed, trying attribute query",
                "GeoAI Pro",
                Qgis.Warning
            )
            return self._execute_attribute_query(sql, layer)

        except Exception as e:
            return {"error": str(e)}

    def _execute_direct_postgres(self, sql: str) -> Dict:
        """Execute SQL directly on PostgreSQL using .env credentials."""

        env_creds = self._load_db_credentials()

        if not env_creds.get("database"):
            return {
                "error": "No database configured. Please set DB_NAME in your .env file.\n"
                        "Example: DB_NAME=your_database_name"
            }

        host = env_creds.get("host", "localhost")
        port = int(env_creds.get("port", 5432))
        database = env_creds.get("database", "")
        username = env_creds.get("user", "")
        password = env_creds.get("password", "")

        # Log connection details for debugging
        QgsMessageLog.logMessage(
            f"Direct PostgreSQL connection - Host: {host}, Port: {port}, Database: {database}, User: {username}",
            "GeoAI Pro",
            Qgis.Info
        )

        connection_name = f"GeoAI_Direct_{database}_{username}"
        if QSqlDatabase.contains(connection_name):
            QSqlDatabase.removeDatabase(connection_name)

        db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        db.setHostName(host)
        db.setPort(port)
        db.setDatabaseName(database)
        db.setUserName(username)
        db.setPassword(password)

        if not db.open():
            error_text = db.lastError().text()
            # Provide helpful error message
            if "does not exist" in error_text:
                return {
                    "error": f"Database '{database}' does not exist.\n\n"
                            f"Please check your .env file and update DB_NAME to the correct database name.\n"
                            f"Current settings: Host={host}, Port={port}, Database={database}\n\n"
                            f"To find available databases, you can run:\n"
                            f"SELECT datname FROM pg_database WHERE datistemplate = false;\n\n"
                            f"Original error: {error_text}"
                }
            return {
                "error": f"Database connection failed: {error_text}\n"
                        f"Connection details: Host={host}, Port={port}, Database={database}, User={username}"
            }

        # Split multiple statements and execute each
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        all_results = []
        total_affected = 0

        for stmt in statements:
            if not stmt:
                continue

            query = QSqlQuery(db)
            if not query.exec_(stmt):
                error = query.lastError().text()
                db.close()
                QSqlDatabase.removeDatabase(connection_name)
                return {"error": error, "sql": stmt}

            # Check if it's a SELECT query
            if stmt.strip().upper().startswith("SELECT"):
                record = query.record()
                field_names = [record.fieldName(i) for i in range(record.count())]

                while query.next():
                    row = {name: query.value(i) for i, name in enumerate(field_names)}
                    all_results.append(row)
            else:
                # For INSERT, UPDATE, DELETE, CREATE, DROP, etc.
                total_affected += query.numRowsAffected()

        db.close()
        QSqlDatabase.removeDatabase(connection_name)

        if all_results:
            return {"success": True, "rows": all_results, "row_count": len(all_results)}
        else:
            return {
                "success": True,
                "rows": [
                    {
                        "message": f"Query executed successfully. {total_affected} rows affected."
                    }
                ],
                "row_count": 1,
            }

    def _execute_postgres(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute SQL on PostgreSQL/PostGIS database."""

        uri = QgsDataSourceUri(layer.source())

        # Load fallback credentials from .env
        env_creds = self._load_db_credentials()

        # Use layer URI values, fall back to .env if not available
        host = uri.host() or env_creds.get("host", "localhost")
        port = int(uri.port()) if uri.port() else int(env_creds.get("port", 5432))
        database = uri.database() or env_creds.get("database", "")
        username = uri.username() or env_creds.get("user", "")
        password = uri.password() or env_creds.get("password", "")

        # Validate database name
        if not database:
            return {
                "error": "Database name not found. Please check your layer connection or set DB_NAME in .env file."
            }

        # Log connection details for debugging
        QgsMessageLog.logMessage(
            f"Connecting to PostgreSQL - Host: {host}, Port: {port}, Database: {database}, User: {username}",
            "GeoAI Pro",
            Qgis.Info
        )

        connection_name = f"GeoAI_{database}_{username}"
        if QSqlDatabase.contains(connection_name):
            QSqlDatabase.removeDatabase(connection_name)

        db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        db.setHostName(host)
        db.setPort(port)
        db.setDatabaseName(database)
        db.setUserName(username)
        db.setPassword(password)

        if not db.open():
            error_text = db.lastError().text()
            # Provide helpful error message
            if "does not exist" in error_text:
                return {
                    "error": f"Database '{database}' does not exist. Please check:\n"
                            f"1. The database name in your layer connection\n"
                            f"2. The DB_NAME in your .env file\n"
                            f"3. That the database exists on the server\n\n"
                            f"Connection details: Host={host}, Port={port}, Database={database}\n"
                            f"Original error: {error_text}"
                }
            return {
                "error": f"Database connection failed: {error_text}\n"
                        f"Connection details: Host={host}, Port={port}, Database={database}, User={username}"
            }

        query = QSqlQuery(db)
        if not query.exec_(sql):
            error = query.lastError().text()
            db.close()
            QSqlDatabase.removeDatabase(connection_name)
            return {"error": error, "sql": sql}

        # Collect query results
        results = []
        record = query.record()
        field_names = [record.fieldName(i) for i in range(record.count())]

        while query.next():
            row = {name: query.value(i) for i, name in enumerate(field_names)}
            results.append(row)

        db.close()
        QSqlDatabase.removeDatabase(connection_name)

        return {"success": True, "rows": results, "row_count": len(results)}

    def _execute_spatialite(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute SQL on SpatiaLite or GeoPackage."""
        import sqlite3
        import os

        # Extract file path from layer source
        source = layer.source().split("|")[0]
        
        # Clean up the source path (remove query parameters, etc.)
        if "?" in source:
            source = source.split("?")[0]
        if "#" in source:
            source = source.split("#")[0]
        
        # Validate file exists and is a database
        if not os.path.exists(source):
            return {
                "error": f"Database file not found: {source}. Please check the layer source path.",
                "sql": sql
            }
        
        if not os.path.isfile(source):
            return {
                "error": f"Source is not a file: {source}. Please check the layer source path.",
                "sql": sql
            }

        try:
            # Try to open as SQLite database to validate
            test_conn = sqlite3.connect(source)
            test_conn.execute("SELECT 1")
            test_conn.close()
        except sqlite3.Error as e:
            return {
                "error": f"File is not a valid database: {source}. Error: {str(e)}. Please ensure the layer is connected to a valid SpatiaLite or GeoPackage database.",
                "sql": sql
            }

        try:
            conn = sqlite3.connect(source)
            conn.enable_load_extension(True)
            try:
                conn.load_extension("mod_spatialite")
            except Exception:
                pass

            cursor = conn.cursor()
            cursor.execute(sql)

            if sql.strip().upper().startswith("SELECT"):
                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                conn.close()
                return {"success": True, "rows": rows, "row_count": len(rows)}

            conn.commit()
            conn.close()
            return {"success": True, "message": "Query executed successfully"}

        except sqlite3.Error as e:
            return {
                "error": f"SQLite error: {str(e)}. Please check your SQL syntax and database connection.",
                "sql": sql
            }
        except Exception as e:
            return {
                "error": f"Error executing query: {str(e)}. Source: {source}",
                "sql": sql
            }

    def _execute_attribute_query(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute simple attribute queries on in-memory or shapefile layers."""
        import re

        where_match = re.search(r"WHERE\s+(.+?)(?:ORDER|LIMIT|$)", sql, re.IGNORECASE)
        if not where_match:
            return {"error": "Unsupported query format for non-database layer."}

        where_clause = where_match.group(1).strip()
        layer.selectByExpression(where_clause)

        results = []
        for feature in layer.selectedFeatures():
            row = {field.name(): feature[field.name()] for field in layer.fields()}
            results.append(row)

        return {"success": True, "rows": results, "row_count": len(results)}

    def create_layer_from_sql(self, sql: str, layer_name: str) -> Dict:
        """Create a temporary memory layer from SQL query results."""
        result = self.execute_sql(sql)
        if "error" in result:
            return result
        if not result.get("rows"):
            return {"error": "Query returned no results"}

        # Define memory layer schema
        uri = "Point?crs=epsg:4326"
        for field_name in result["rows"][0].keys():
            uri += f"&field={field_name}:string"

        layer = QgsVectorLayer(uri, layer_name, "memory")
        provider = layer.dataProvider()

        features = []
        for row in result["rows"]:
            feature = QgsFeature()
            feature.setAttributes(list(row.values()))
            features.append(feature)

        provider.addFeatures(features)
        layer.updateExtents()
        self.project.addMapLayer(layer)

        return {
            "success": True,
            "message": f"Layer '{layer_name}' created with {len(features)} features",
        }
