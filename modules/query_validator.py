"""
Query Validator - Validates SQL queries against actual database schema
"""

from typing import Dict


class QueryValidator:
    """Validates SQL queries against actual database schema."""

    def __init__(self, sql_executor):
        self.sql_executor = sql_executor

    def validate_query(self, sql: str, context: Dict) -> Dict:
        """Validate that query uses only existing fields."""

        import re

        # Extract field names from SQL
        field_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        fields_in_query = set(re.findall(field_pattern, sql))

        # Remove SQL keywords
        sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'AS', 'JOIN',
            'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'GROUP', 'BY',
            'ORDER', 'LIMIT', 'OFFSET', 'HAVING', 'DISTINCT', 'COUNT',
            'SUM', 'AVG', 'MIN', 'MAX', 'ST_Area', 'ST_Distance'
        }
        fields_in_query = {f for f in fields_in_query if f.upper() not in sql_keywords}

        # Get all available fields
        available_fields = set()
        table_fields = context.get("table_fields", {})
        for table_name, fields in table_fields.items():
            available_fields.update(fields)

        # Find missing fields
        missing_fields = fields_in_query - available_fields - {'geom', 'geometry', 'wkb_geometry'}

        if missing_fields:
            # Try to suggest alternatives
            suggestions = self._suggest_alternatives(missing_fields, available_fields)

            return {
                "valid": False,
                "missing_fields": list(missing_fields),
                "suggestions": suggestions,
                "message": f"Fields not found: {', '.join(missing_fields)}"
            }

        return {"valid": True, "message": "Query appears valid"}

    def _suggest_alternatives(self, missing_fields: set, available_fields: set) -> Dict:
        """Suggest similar field names or calculations."""

        from difflib import get_close_matches

        suggestions = {}
        for missing in missing_fields:
            # Find similar field names
            matches = get_close_matches(missing.lower(),
                                       [f.lower() for f in available_fields],
                                       n=3, cutoff=0.6)

            if matches:
                suggestions[missing] = matches
            else:
                # Suggest calculations for common fields
                if missing.lower() in ['area', 'size']:
                    suggestions[missing] = ["Use ST_Area(geom) to calculate area"]
                elif missing.lower() in ['length', 'perimeter']:
                    suggestions[missing] = ["Use ST_Length(geom) or ST_Perimeter(geom)"]
                elif missing.lower() in ['distance']:
                    suggestions[missing] = ["Use ST_Distance(geom1, geom2)"]

        return suggestions

