"""Database connection and management utilities."""

from sqlalchemy import create_engine, text
from langchain_community.utilities.sql_database import SQLDatabase
import logging

class DatabaseManager:
    """Manages database connections and provides database utilities."""
    
    def __init__(self, database_url: str):
        """Initialize database manager with connection URL."""
        self.database_url = database_url
        self._engine = None
        self._db = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    @property
    def engine(self):
        """Get or create SQLAlchemy engine with connection pooling."""
        if self._engine is None:
            try:
                # Create engine with connection pooling and timeout settings
                self._engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,  # Verify connections before use
                    pool_recycle=3600,   # Recycle connections every hour
                    connect_args={
                        "connect_timeout": 10,  # 10 second connection timeout
                        "application_name": "NaturalLanguageSQLAgent"
                    }
                )
                self.logger.info("Database engine created successfully")
            except Exception as e:
                self.logger.error(f"Failed to create database engine: {e}")
                raise
        return self._engine
    
    @property
    def db(self):
        """Get or create LangChain SQLDatabase instance."""
        if self._db is None:
            try:
                self._db = SQLDatabase(self.engine)
                self.logger.info("LangChain SQLDatabase instance created")
            except Exception as e:
                self.logger.error(f"Failed to create SQLDatabase instance: {e}")
                raise
        return self._db
    
    def test_connection(self) -> bool:
        """Test if database connection is working."""
        try:
            with self.engine.connect() as conn:
                # Execute a simple test query
                result = conn.execute(text("SELECT 1"))
                # Fetch the result to ensure the query actually executed
                result.fetchone()
                self.logger.info("Database connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get information about the database connection."""
        try:
            with self.engine.connect() as conn:
                # Get database version
                version_result = conn.execute(text("SELECT version()"))
                version = version_result.fetchone()[0]
                
                # Get current database name
                db_result = conn.execute(text("SELECT current_database()"))
                db_name = db_result.fetchone()[0]
                
                return {
                    "connected": True,
                    "database_name": db_name,
                    "version": version,
                    "url": self.database_url.replace(
                        self.database_url.split('@')[0].split('//')[1].split(':')[0] + ':' + 
                        self.database_url.split('@')[0].split('//')[1].split(':')[1].split('@')[0], 
                        '***:***'
                    ) if '@' in self.database_url else self.database_url
                }
        except Exception as e:
            self.logger.error(f"Failed to get connection info: {e}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connections."""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                self.logger.info("Database engine disposed")
            if self._db:
                self._db = None
                self.logger.info("SQLDatabase instance cleared")
        except Exception as e:
            self.logger.error(f"Error closing database connections: {e}")
