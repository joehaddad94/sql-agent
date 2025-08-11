#!/usr/bin/env python3
from src.core.sql_agent import SQLAgent
import sys

def main():
    try:
        print("Initializing SQL Agent...")
        agent = SQLAgent()
        
        print("\nDatabase Information:")
        db_info = agent.get_database_info()
        if "error" in db_info:
            print(f"Error: {db_info['error']}")
            return
        
        print(f"Connection Status: {'Connected' if db_info['connection_status'] else 'Failed'}")
        print(f"Available Tables: {', '.join(db_info['tables']) if db_info['tables'] else 'None'}")
        
        query = "How many applications did I get from two months ago until now?"
        print(f"\nProcessing Query: {query}")
        
        result = agent.process_query(query)
        
        if result["success"]:
            print("Query processed successfully!")
            print(f"Generated SQL: {result['generated_sql']}")
            print(f"Result: {result['result']}")
        else:
            print(f"Query failed: {result['error']}")
            if "generated_sql" in result:
                print(f"Generated SQL: {result['generated_sql']}")
        
        agent.close()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
