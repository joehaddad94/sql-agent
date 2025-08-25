import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@host:port/dbname")
    
    # LangSmith Configuration
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "natural-language-sql-agent")
    LANGSMITH_TRACING_V2 = os.getenv("LANGSMITH_TRACING_V2", "true").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not cls.DATABASE_URL or cls.DATABASE_URL == "postgresql://username:password@host:port/dbname":
            raise ValueError("DATABASE_URL environment variable must be set to a valid database connection string")
        
        return True
    
    @classmethod
    def setup_langsmith(cls):
        """Set up LangSmith environment variables if API key is provided."""
        if cls.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = str(cls.LANGSMITH_TRACING_V2).lower()
            os.environ["LANGCHAIN_ENDPOINT"] = cls.LANGSMITH_ENDPOINT
            os.environ["LANGCHAIN_API_KEY"] = cls.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = cls.LANGSMITH_PROJECT
            return True
        return False
