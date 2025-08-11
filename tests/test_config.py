"""Tests for the configuration module."""

import unittest
from unittest.mock import patch
import os
from src.utils.config import Config

class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb'
    })
    def test_config_loading(self):
        """Test that configuration loads from environment variables."""
        # Reload config
        Config.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        Config.DATABASE_URL = os.getenv("DATABASE_URL")
        
        self.assertEqual(Config.OPENAI_API_KEY, 'test_key')
        self.assertEqual(Config.DATABASE_URL, 'postgresql://test:test@localhost:5432/testdb')
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb'
    })
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        # Reload config
        Config.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        Config.DATABASE_URL = os.getenv("DATABASE_URL")
        
        self.assertTrue(Config.validate())
    
    def test_config_validation_missing_api_key(self):
        """Test configuration validation with missing API key."""
        Config.OPENAI_API_KEY = None
        Config.DATABASE_URL = 'postgresql://test:test@localhost:5432/testdb'
        
        with self.assertRaises(ValueError):
            Config.validate()

if __name__ == '__main__':
    unittest.main()
