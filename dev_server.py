#!/usr/bin/env python3
"""
Development Server with Hot Reload for Natural Language SQL Agent
"""

import sys
import os
import time
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class AgentReloader(FileSystemEventHandler):
    """Watches for file changes and reloads the agent."""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.last_reload = time.time()
        self.reload_cooldown = 5  # Minimum seconds between reloads
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Avoid reloading too frequently
        current_time = time.time()
        if current_time - self.last_reload < self.reload_cooldown:
            return
        
        print(f"\n🔄 File changed: {os.path.basename(event.src_path)}")
        print("🔄 Reloading agent...")
        
        try:
            self.agent_manager.reload_agent()
            self.last_reload = current_time
            print("✅ Agent reloaded successfully!")
            print("💬 You can now continue with your queries...")
        except Exception as e:
            print(f"❌ Failed to reload agent: {e}")

class AgentManager:
    """Manages the SQL Agent with reloading capabilities."""
    
    def __init__(self):
        self.agent = None
        self.reload_agent()
    
    def reload_agent(self):
        """Reload the agent by reimporting modules."""
        try:
            # Clear any cached imports
            importlib.invalidate_caches()
            
            # Reimport the agent
            from src.core.sql_agent import SQLAgent
            self.agent = SQLAgent()
            print("✅ Agent loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading agent: {e}")
            if self.agent is None:
                raise
    
    def get_agent(self):
        """Get the current agent instance."""
        return self.agent
    
    def close(self):
        """Close the current agent."""
        if self.agent:
            self.agent.close()

def main():
    """Main development server function."""
    
    print("🚀 Natural Language SQL Agent - Development Server")
    print("=" * 50)
    print("📁 Watching for file changes...")
    print("🔄 Agent will auto-reload when you save changes")
    print("💡 Type 'quit' to exit")
    print("-" * 50)
    
    try:
        # Initialize agent manager
        agent_manager = AgentManager()
        
        # Set up file watching
        event_handler = AgentReloader(agent_manager)
        observer = Observer()
        observer.schedule(event_handler, path='src', recursive=True)
        observer.start()
        
        # Interactive mode
        while True:
            try:
                query = input("\n💬 Enter your natural language query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print(f"\n🔍 Processing: '{query}'")
                print("⏳ Please wait...")
                
                # Get the current agent (might have been reloaded)
                agent = agent_manager.get_agent()
                
                # Process the query
                result = agent.process_query(query)
                
                if result["success"]:
                    print("✅ Query processed successfully!")
                    print(f"📋 Answer: {result['answer']}")
                    if result.get('sql_query_used'):
                        print(f"🔍 SQL Query Used: {result['sql_query_used']}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("🔄 Try reloading the agent or check your changes")
    
    except Exception as e:
        print(f"❌ Failed to start development server: {e}")
        print("\n💡 Make sure you have:")
        print("  1. Set OPENAI_API_KEY in your .env file")
        print("  2. Set DATABASE_URL in your .env file")
        print("  3. Installed all requirements: pip install -r requirements.txt")
    
    finally:
        # Clean up
        if 'agent_manager' in locals():
            agent_manager.close()
        if 'observer' in locals():
            observer.stop()
            observer.join()

if __name__ == "__main__":
    main()
