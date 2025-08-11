"""Database connection and management utilities."""

from sqlalchemy import create_engine, text
from langchain_community.utilities.sql_database import SQLDatabase
from typing import Optional

class DatabaseManager:
    """Manages database connections and provides database utilities."""
    
    def __init__(self, database_url: str):
        """Initialize database manager with connection URL."""
        self.database_url = database_url
        self._engine = None
        self._db = None
    
    @property
    def engine(self):
        """Get or create SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(self.database_url)
        return self._engine
    
    @property
    def db(self):
        """Get or create LangChain SQLDatabase instance."""
        if self._db is None:
            self._db = SQLDatabase(self.engine)
        return self._db
    
    def test_connection(self) -> bool:
        """Test if database connection is working."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
        self._db = None
