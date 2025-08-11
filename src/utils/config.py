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
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not cls.DATABASE_URL or cls.DATABASE_URL == "postgresql://username:password@host:port/dbname":
            raise ValueError("DATABASE_URL environment variable must be set to a valid database connection string")
        
        return True
