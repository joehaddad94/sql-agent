"""Example usage of the SQL Agent."""

from src.core.sql_agent import SQLAgent

def example_usage():
    """Demonstrate basic usage of the SQL Agent."""
    
    # Initialize the agent
    agent = SQLAgent()
    
    # Example queries
    queries = [
        "How many applications did I get from the start of this month until now?",
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        try:
            result = agent.process_query(query)
            
            if result["success"]:
                print(f"✅ Success!")
                print(f"Generated SQL: {result['generated_sql']}")
                print(f"Result: {result['result']}")
            else:
                print(f"❌ Failed: {result['error']}")
                if "generated_sql" in result:
                    print(f"Generated SQL: {result['generated_sql']}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Get database information
    print(f"\n{'='*50}")
    print("Database Information")
    print(f"{'='*50}")
    
    db_info = agent.get_database_info()
    if "error" not in db_info:
        print(f"Connection: {'✅ Connected' if db_info['connection_status'] else '❌ Failed'}")
        print(f"Tables: {', '.join(db_info['tables']) if db_info['tables'] else 'None'}")
        
        if db_info['table_summary']:
            print("\nTable Summary:")
            for table, count in db_info['table_summary'].items():
                print(f"  {table}: {count} rows")
    else:
        print(f"Error: {db_info['error']}")
    
    # Clean up
    agent.close()

if __name__ == "__main__":
    example_usage()
