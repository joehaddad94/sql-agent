from typing import Dict, Any, Union
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from src.database.connection import DatabaseManager
from src.database.schema import SchemaInspector
from src.utils.config import Config

class SQLAgent(Runnable):
    
    def __init__(self):
        # Validate configuration
        Config.validate()
        
        # Initialize components
        self.db_manager = DatabaseManager(Config.DATABASE_URL)
        self.schema_inspector = SchemaInspector(self.db_manager)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.0,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Create SQL Database Toolkit
        self.toolkit = SQLDatabaseToolkit(db=self.db_manager.db, llm=self.llm)
        self.tools = self.toolkit.get_tools()
        
        # Create system message
        self.system_message = """
            You are an agent designed to interact with a SQL database for an educational application system.
            Given an input question, create a syntactically correct {dialect} query to run,
            then look at the results of the query and return the answer. Unless the user
            specifies a specific number of examples they wish to obtain, always limit your
            query to at most {top_k} results.

            You can order the results by a relevant column to return the most interesting
            examples in the database. Never query for all the columns from a specific table,
            only ask for the relevant columns given the question.

            You MUST double check your query before executing it. If you get an error while
            executing a query, rewrite the query and try again.

            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
            database.

            To start you should ALWAYS look at the tables in the database to see what you
            can query. Do NOT skip this step.

            Then you should query the schema of the most relevant tables.

            CRITICAL TABLE SELECTION GUIDELINES:
            - For applications and submissions: Use 'application_news' table (NOT 'applicants')
            - For programs and courses: Use 'programs' table
            - For application cycles and dates: Use 'cycles' table
            - For user information: Use 'up_users' table
            - For application components and details: Use 'application_news_*_links' tables
            - For decision dates: Use 'decision_dates' table
            - For enrolled applications: Use 'enrolled_applications' table

            IMPORTANT BUSINESS LOGIC:
            - Applications are stored in 'application_news' table, not 'applicants'
            - Use 'created_at' field for date-based queries on applications
            - Application status and acceptance are tracked in 'application_news' table
            - Programs and courses are managed in 'programs' table
            - Application cycles (academic periods) are in 'cycles' table
            - User information is in 'up_users' table, not 'admin_users'

            When answering questions about applications, always use the 'application_news' table
            and its related link tables for comprehensive information.
            """.format(
            dialect="PostgreSQL",  # Assuming PostgreSQL based on psycopg2 in requirements
            top_k=1,
        )
        
        # Create the agent
        self.agent_executor = create_react_agent(self.llm, self.tools, prompt=self.system_message)
    
    def process_query(self, natural_language_query: str) -> Dict[str, Any]:
        """Process a natural language query using the LangChain agent and return results."""
        try:
            # Execute the agent with the query
            result = self.agent_executor.invoke({
                "messages": [{"role": "user", "content": natural_language_query}]
            })
            
            # Extract the final answer and SQL query from the messages
            final_answer = ""
            sql_query_used = ""
            
            if "messages" in result:
                # Look through all messages to find the final answer and SQL query
                for message in result["messages"]:
                    if hasattr(message, 'content') and message.content:
                        # Check if message has no tool calls (None, False, or empty list)
                        has_tool_calls = bool(hasattr(message, 'tool_calls') and message.tool_calls and len(message.tool_calls) > 0)
                        
                        if not has_tool_calls:
                            if message.content and message.content.strip():
                                final_answer = message.content
                        
                        # Look for SQL queries in tool calls
                        if has_tool_calls:
                            for tool_call in message.tool_calls:
                                if tool_call.get('function', {}).get('name') == 'sql_db_query':
                                    # Extract the SQL query from the tool call arguments
                                    try:
                                        import json
                                        args = json.loads(tool_call['function']['arguments'])
                                        if 'query' in args:
                                            sql_query_used = args['query']
                                    except Exception as e:
                                        print(f"Warning: Error parsing tool call args: {e}")
            
            # If no clear answer found, try to extract from the result structure
            if not final_answer:
                # Look for the last message with content that's not a tool call
                for message in reversed(result["messages"]):
                    if hasattr(message, 'content') and message.content and message.content.strip():
                        # Check if message has no tool calls (None, False, or empty list)
                        has_tool_calls = bool(hasattr(message, 'tool_calls') and message.tool_calls and len(message.tool_calls) > 0)
                        
                        if not has_tool_calls:
                            final_answer = message.content
                            break
                
                if not final_answer:
                    final_answer = "No clear answer generated"
            
            return {
                "success": True,
                "natural_language_query": natural_language_query,
                "answer": final_answer,
                "sql_query_used": sql_query_used,
                "raw_result": result  # Keep raw result for debugging if needed
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database."""
        try:
            # Get basic connection status
            connection_status = self.db_manager.test_connection()
            
            # Get detailed connection info
            connection_info = self.db_manager.get_connection_info()
            
            # Get schema information
            tables = self.schema_inspector.get_table_names()
            table_summary = self.schema_inspector.get_table_summary()
            
            return {
                "connection_status": connection_status,
                "connection_details": connection_info,
                "tables": tables,
                "table_summary": table_summary,
                "available_tools": [tool.name for tool in self.tools]
            }
        except Exception as e:
            return {
                "error": f"Failed to get database info: {str(e)}"
            }
    
    def close(self):
        """Close database connections."""
        self.db_manager.close()
    
    # LangServe Runnable interface methods
    def invoke(self, input_data: Union[str, Dict[str, Any]], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke the agent with input data. This is the main entry point for LangServe."""
        if isinstance(input_data, str):
            # Direct string input
            return self.process_query(input_data)
        elif isinstance(input_data, dict) and "query" in input_data:
            # Dictionary with query key
            return self.process_query(input_data["query"])
        elif isinstance(input_data, dict) and "input" in input_data:
            # LangServe input format
            return self.process_query(input_data["input"])
        elif hasattr(input_data, 'query'):
            # Pydantic model with query attribute
            return self.process_query(input_data.query)
        elif hasattr(input_data, 'input'):
            # Pydantic model with input attribute
            return self.process_query(input_data.input)
        elif isinstance(input_data, dict) and "messages" in input_data:
            # LangChain message format
            if input_data["messages"] and len(input_data["messages"]) > 0:
                last_message = input_data["messages"][-1]
                if hasattr(last_message, 'content'):
                    return self.process_query(last_message.content)
                elif isinstance(last_message, dict) and "content" in last_message:
                    return self.process_query(last_message["content"])
        
        # Fallback
        return {
            "success": False,
            "error": f"Unsupported input format. Expected string, dict with 'query' or 'input', or Pydantic model with 'query' or 'input' attribute, got {type(input_data)}"
        }
    
    def stream(self, input_data: Union[str, Dict[str, Any]], config: Dict[str, Any] = None):
        """Stream responses from the agent. For now, just return the full response."""
        result = self.invoke(input_data, config)
        yield result
