from langchain_openai import ChatOpenAI
from typing import Optional
from ..utils.config import Config

class SQLQueryGenerator:
    """Generates SQL queries from natural language using LLM."""
    
    def __init__(self):
        """Initialize the query generator."""
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
    
    def generate_sql_query(self, natural_language_query: str, database_schema: str) -> Optional[str]:
        """Generate SQL query from natural language with database schema context."""
        try:
            prompt = self._create_prompt(natural_language_query, database_schema)
            response = self.llm.invoke(prompt)
            
            # Clean the response to remove markdown formatting
            sql_query = response.content.strip()
            
            # Remove markdown code blocks if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]  # Remove ```sql
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]   # Remove ```
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]  # Remove trailing ```
            
            return sql_query.strip()
        except Exception as e:
            print(f"Error generating SQL query: {e}")
            return None
    
    def _create_prompt(self, query: str, schema: str) -> str:
        """Create the prompt for SQL generation."""
        return f"""Given this database schema:
{schema}

And this question: {query}

Generate a SQL query to answer it. Use only the tables and columns that exist in the schema above.

IMPORTANT TABLE SELECTION GUIDELINES:
- For applications and submissions: Use 'application_news' table (not 'applicants')
- For programs and courses: Use 'programs' table
- For application cycles and dates: Use 'cycles' table
- For user information: Use 'up_users' table

Return only the SQL query, nothing else."""
    
    def validate_sql(self, sql_query: str) -> bool:
        if not sql_query:
            return False
        
        # Basic checks
        sql_lower = sql_query.lower().strip()
        
        # Should start with SELECT, INSERT, UPDATE, DELETE
        if not any(sql_lower.startswith(keyword) for keyword in ['select', 'insert', 'update', 'delete']):
            return False
        
        # Should not contain multiple statements
        if ';' in sql_query and sql_query.count(';') > 1:
            return False
        
        return True
