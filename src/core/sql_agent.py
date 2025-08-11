"""Core SQL Agent that orchestrates natural language to SQL query processing."""

from typing import Optional, Dict, Any
from ..database.connection import DatabaseManager
from ..database.schema import SchemaInspector
from ..llm.query_generator import SQLQueryGenerator
from ..utils.config import Config

class SQLAgent:
    """Main SQL Agent that processes natural language queries and executes SQL."""
    
    def __init__(self):
        """Initialize the SQL Agent."""
        # Validate configuration
        Config.validate()
        
        # Initialize components
        self.db_manager = DatabaseManager(Config.DATABASE_URL)
        self.schema_inspector = SchemaInspector(self.db_manager)
        self.query_generator = SQLQueryGenerator()
    
    def process_query(self, natural_language_query: str) -> Dict[str, Any]:
        """Process a natural language query and return results."""
        try:
            # Get database schema
            schema = self.schema_inspector.get_full_schema()
            if not schema or schema.startswith("Error"):
                return {
                    "success": False,
                    "error": "Failed to retrieve database schema",
                    "schema_error": schema
                }
            
            # Generate SQL query
            sql_query = self.query_generator.generate_sql_query(natural_language_query, schema)
            if not sql_query:
                return {
                    "success": False,
                    "error": "Failed to generate SQL query"
                }
            
            # Validate SQL query
            if not self.query_generator.validate_sql(sql_query):
                return {
                    "success": False,
                    "error": "Generated SQL query is invalid",
                    "generated_sql": sql_query
                }
            
            # Execute SQL query
            result = self.db_manager.db.run(sql_query)
            
            return {
                "success": True,
                "natural_language_query": natural_language_query,
                "generated_sql": sql_query,
                "result": result,
                "schema_used": schema
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database."""
        try:
            return {
                "connection_status": self.db_manager.test_connection(),
                "tables": self.schema_inspector.get_table_names(),
                "table_summary": self.schema_inspector.get_table_summary()
            }
        except Exception as e:
            return {
                "error": f"Failed to get database info: {str(e)}"
            }
    
    def close(self):
        """Close database connections."""
        self.db_manager.close()
