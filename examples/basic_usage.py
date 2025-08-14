#!/usr/bin/env python3
"""
Basic usage example for the Natural Language SQL Agent.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.sql_agent import SQLAgent

def main():
    """Main function to demonstrate the SQL Agent."""
    
    try:
        # Initialize the SQL Agent
        print("Initializing SQL Agent...")
        agent = SQLAgent()
        
        # Get database information
        print("\nGetting database information...")
        db_info = agent.get_database_info()
        print(f"Connection status: {db_info.get('connection_status')}")
        print(f"Available tables: {db_info.get('tables', [])}")
        print(f"Available tools: {db_info.get('available_tools', [])}")
        
        # Example natural language query
        query = "Show me the first 3 rows from the users table"
        print(f"\nProcessing query: '{query}'")
        
        # Process the query
        result = agent.process_query(query)
        
        if result["success"]:
            print("Query processed successfully!")
            print(f"Answer: {result['answer']}")
            if result.get('sql_query_used'):
                print(f"SQL Query Used: {result['sql_query_used']}")
        else:
            print(f"Error: {result['error']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        if 'agent' in locals():
            agent.close()

if __name__ == "__main__":
    main()
