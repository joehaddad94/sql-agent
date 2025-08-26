#!/usr/bin/env python3
"""
Natural Language SQL Agent - Main Entry Point
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.sql_agent import SQLAgent

def main():
    """Main function to run the SQL Agent."""
    
    print("🚀 Natural Language SQL Agent")
    
    try:
        # Initialize the SQL Agent
        agent = SQLAgent()
        print("✅ SQL Agent ready")
        
        # Get database information
        db_info = agent.get_database_info()
        
        if "error" not in db_info:
            print(f"📊 Database: {'✅ Connected' if db_info['connection_status'] else '❌ Failed'}")
        else:
            print(f"❌ Database error: {db_info['error']}")
            return
        
        # Interactive query mode
        print("💬 Interactive mode (type 'quit' to exit)")
        
        while True:
            try:
                query = input("\nEnter your natural language query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print(f"🔍 Processing: {query}")
                
                # Process the query
                result = agent.process_query(query)
                
                if result["success"]:
                    print(f"✅ {result['answer']}")
                    if result.get('sql_query_used'):
                        print(f"🔍 SQL: {result['sql_query_used']}")
                else:
                    print(f"❌ {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize SQL Agent: {e}")
        print("\n💡 Make sure you have:")
        print("  1. Set OPENAI_API_KEY in your .env file")
        print("  2. Set DATABASE_URL in your .env file")
        print("  3. Installed all requirements: pip install -r requirements.txt")
    
    finally:
        # Clean up
        if 'agent' in locals():
            agent.close()

if __name__ == "__main__":
    main()
