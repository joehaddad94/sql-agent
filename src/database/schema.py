"""Database schema inspection utilities."""

from typing import List, Dict, Optional
from .connection import DatabaseManager

class SchemaInspector:
    """Inspects and provides database schema information."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize schema inspector with database manager."""
        self.db_manager = db_manager
    
    def get_table_names(self) -> List[str]:
        """Get all available table names."""
        try:
            # Use direct SQL query instead of the problematic method
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
            result = self.db_manager.db.run(query)
            
            # Parse the result to extract table names
            if result:
                # The result is a single string containing Python tuple format
                # Remove the outer brackets and split by ), (
                content = result.strip()
                
                # Remove outer brackets if present
                if content.startswith('[') and content.endswith(']'):
                    content = content[1:-1]
                
                # Split by ), ( to get individual tuples
                # This handles the format: ('table1',), ('table2',), ('table3',)
                parts = content.split("), (")
                
                table_names = []
                for part in parts:
                    # Clean up each part
                    part = part.strip()
                    
                    # Remove leading ( and trailing )
                    if part.startswith('('):
                        part = part[1:]
                    if part.endswith(')'):
                        part = part[:-1]
                    
                    # Remove quotes and trailing comma
                    if part.startswith("'") and part.endswith("',"):
                        part = part[1:-2]  # Remove ' and ,
                    elif part.startswith("'") and part.endswith("'"):
                        part = part[1:-1]  # Remove ' only
                    
                    if part and part not in table_names:  # Avoid duplicates
                        table_names.append(part)
                
                return table_names
            return []
        except Exception as e:
            print(f"Error getting table names: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Optional[str]:
        """Get detailed information about a specific table."""
        try:
            # Use direct SQL query to get table structure
            query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
            """
            result = self.db_manager.db.run(query)
            
            if result:
                return f"Table: {table_name}\nColumns:\n{result}"
            else:
                return f"Table: {table_name}\nNo columns found"
                
        except Exception as e:
            print(f"Error getting table info for {table_name}: {e}")
            return None
    
    def get_full_schema(self) -> str:
        """Get complete database schema information."""
        try:
            table_names = self.get_table_names()
            if not table_names:
                return "No tables found in database"
            
            schema_info = []
            for table in table_names:
                table_info = self.get_table_info(table)
                if table_info:
                    schema_info.append(f"Table: {table}\n{table_info}\n")
            
            return "\n".join(schema_info)
        except Exception as e:
            print(f"Error getting full schema: {e}")
            return f"Error retrieving schema: {e}"
    
    def get_table_summary(self) -> Dict[str, int]:
        """Get a summary of tables and their row counts."""
        try:
            summary = {}
            table_names = self.get_table_names()
            
            for table in table_names:
                try:
                    # Get row count for each table
                    result = self.db_manager.db.run(f"SELECT COUNT(*) FROM {table}")
                    count = result.strip() if result else "0"
                    summary[table] = count
                except Exception:
                    summary[table] = "Error getting count"
            
            return summary
        except Exception as e:
            print(f"Error getting table summary: {e}")
            return {}
