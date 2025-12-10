"""
Smart Assistant - Intelligent assistant for QGIS operations with layer-specific suggestions
"""

from qgis.core import QgsProject, QgsVectorLayer
from typing import Dict, List


class SmartAssistant:
    """Intelligent assistant for QGIS operations"""

    def __init__(self, llm_handler, iface, sql_executor=None):
        self.llm = llm_handler
        self.iface = iface
        self.project = QgsProject.instance()
        self.sql_executor = sql_executor

    def analyze_project(self) -> Dict:
        """Analyze current project and provide insights"""
        try:
            layers = self.project.mapLayers()
            analysis = {
                "total_layers": len(layers),
                "vector_layers": 0,
                "raster_layers": 0,
                "total_features": 0,
                "crs_list": set(),
                "geometry_types": {}
            }

            for layer_id, layer in layers.items():
                try:
                    if isinstance(layer, QgsVectorLayer):
                        analysis["vector_layers"] += 1
                        analysis["total_features"] += layer.featureCount()
                        crs = layer.crs()
                        if crs.isValid():
                            analysis["crs_list"].add(crs.authid())
                        geom_type = layer.geometryType()
                        analysis["geometry_types"][layer.name()] = geom_type
                    else:
                        analysis["raster_layers"] += 1
                except Exception as e:
                    # Skip problematic layers
                    continue

            return analysis
        except Exception as e:
            # Return minimal analysis on error
            return {
                "total_layers": 0,
                "vector_layers": 0,
                "raster_layers": 0,
                "total_features": 0,
                "crs_list": set(),
                "geometry_types": {}
            }

    def get_suggestions(self, model_provider: str = None, model_name: str = None) -> List[str]:
        """Get smart suggestions based on project state"""
        try:
            # Get comprehensive context from sql_executor if available
            if self.sql_executor:
                try:
                    context = self.sql_executor.get_context()
                except Exception as e:
                    # Fallback if sql_executor fails
                    context = {}
            else:
                context = {}
            
            # Get active layer safely
            active_layer = None
            try:
                active_qgs_layer = self.iface.activeLayer()
                if active_qgs_layer:
                    active_layer = active_qgs_layer.name()
            except Exception:
                pass
            
            # Get CRS safely
            crs = "Unknown"
            try:
                project_crs = self.project.crs()
                if project_crs.isValid():
                    crs = project_crs.authid()
            except Exception:
                pass
            
            # Merge context with safe defaults
            context = {
                "layers": context.get('layers', []),
                "active_layer": context.get('active_layer') or active_layer,
                "crs": context.get('crs') or crs,
                "db_type": context.get('db_type', 'Unknown')
            }

            layers_info = context.get('layers', [])
            active_layer = context.get('active_layer')

            # If no active layer, try to pick the first vector layer if available
            if not active_layer and layers_info:
                for layer in layers_info:
                    if layer.get('geometry_type') is not None:
                        active_layer = layer.get('name')
                        break

            # If still no active layer, return a helpful message
            if not active_layer:
                return [
                    "No active layer found to provide suggestions.",
                    "Please add or select a layer in QGIS to get intelligent suggestions."
                ]

            # Prepare context for LLM, focusing on general suggestions
            try:
                project_analysis = self.analyze_project()
            except Exception:
                project_analysis = {}
            
            llm_context = {
                "active_layer": active_layer,
                "layers": layers_info,
                "crs": context.get('crs'),
                "project_analysis": project_analysis
            }

            # Call LLM with error handling
            if not self.llm:
                return ["Error: LLM handler not available. Please check plugin configuration."]
            
            return self.llm.get_smart_suggestions(
                llm_context, 
                model_provider=model_provider, 
                model_name=model_name
            )
        except Exception as e:
            import traceback
            error_msg = f"Error getting suggestions: {str(e)}"
            return [error_msg]

    def suggest_analysis(self, layer_name: str, model_provider: str = None, model_name: str = None) -> Dict:
        """Suggest analyses for specific layer"""

        layer = self.project.mapLayersByName(layer_name)
        if not layer:
            return {"error": f"Layer '{layer_name}' not found"}

        layer = layer[0]

        if not isinstance(layer, QgsVectorLayer):
            return {"error": "Only vector layers are supported"}

        # Get comprehensive context from sql_executor if available
        if self.sql_executor:
            context = self.sql_executor.get_context()
        else:
            context = {"layers": [], "crs": "Unknown", "db_type": "Unknown"}

        # Find the specific layer's detailed info from the context
        target_layer_info = None
        for l in context.get('layers', []):
            if l.get('name') == layer_name:
                target_layer_info = l
                break

        if not target_layer_info:
            return {"error": f"Detailed info for layer '{layer_name}' not found in context."}

        # Prepare context for LLM
        llm_context = {
            "active_layer": layer_name,
            "layers": context.get('layers', []),
            "target_layer_info": target_layer_info,
            "crs": context.get('crs'),
            "db_type": context.get('db_type'),
            "project_analysis": self.analyze_project()
        }

        prompt = (
            f"Provide a comprehensive analysis and suggest useful operations for the QGIS vector layer named '{layer_name}'.\n"
            "Include summary statistics, potential spatial analyses, attribute insights, and relevant SQL or Python code examples. "
            "Focus on providing a 'full analysis for everything' related to this layer. "
            "Ensure all column names are used exactly as provided and wrapped in double quotes (e.g., SELECT \"Name\" FROM table).\n"
            "Organize the output with clear headings and code blocks."
        )

        suggestions = self.llm.get_smart_suggestions(llm_context, prompt=prompt, 
                                                    model_provider=model_provider, model_name=model_name)

        return {
            "success": True,
            "layer": layer_name,
            "suggestions": suggestions
        }

    def generate_style_from_description(self, layer_name: str, description: str) -> Dict:
        """Generate map styling based on natural language description"""

        layer = self.project.mapLayersByName(layer_name)
        if not layer:
            return {"error": f"Layer '{layer_name}' not found"}

        layer = layer[0]

        prompt = f"""
Generate QGIS styling code for this layer based on the description:

Layer: {layer_name}
Description: {description}

Provide Python code using QgsSymbol, QgsSimpleMarkerSymbolLayer, etc.
"""

        # This would need implementation to generate actual styling code
        return {
            "success": True,
            "message": "Style generation - to be implemented"
        }

