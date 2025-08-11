#!/usr/bin/env python3
"""Main entry point for the SQL Agent application."""

from src.core.sql_agent import SQLAgent
import sys

def main():
    """Main function to run the SQL Agent."""
    try:
        # Initialize the SQL Agent
        print("Initializing SQL Agent...")
        agent = SQLAgent()
        
        # Get database information
        print("\nDatabase Information:")
        db_info = agent.get_database_info()
        if "error" in db_info:
            print(f"Error: {db_info['error']}")
            return
        
        print(f"Connection Status: {'Connected' if db_info['connection_status'] else 'Failed'}")
        print(f"Available Tables: {', '.join(db_info['tables']) if db_info['tables'] else 'None'}")
        
        # Example query
        query = "How many applications did I get from two months ago until now?"
        print(f"\nProcessing Query: {query}")
        
        # Process the query
        result = agent.process_query(query)
        
        if result["success"]:
            print("\n✅ Query processed successfully!")
            print(f"Generated SQL: {result['generated_sql']}")
            print(f"Result: {result['result']}")
        else:
            print(f"\n❌ Query failed: {result['error']}")
            if "generated_sql" in result:
                print(f"Generated SQL: {result['generated_sql']}")
        
        # Close connections
        agent.close()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
