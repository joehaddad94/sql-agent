# SQL Agent with LangChain

This project demonstrates how to use LangChain to create an AI agent that can interact with a PostgreSQL database using natural language queries.

## Features

- Natural language to SQL query conversion
- PostgreSQL database integration
- OpenAI GPT-4o-mini integration
- Error handling and logging
- Environment-based configuration
- Modular, maintainable codebase
- Database schema inspection
- SQL query validation

## Project Structure

```
AI Agent/
├── src/                          # Source code
│   ├── database/                 # Database utilities
│   │   ├── connection.py         # Database connection management
│   │   └── schema.py             # Schema inspection utilities
│   ├── llm/                      # LLM integration
│   │   └── query_generator.py    # SQL query generation
│   ├── core/                     # Core business logic
│   │   └── sql_agent.py          # Main agent orchestration
│   └── utils/                    # Utilities
│       └── config.py             # Configuration management
├── tests/                        # Unit tests
├── examples/                     # Usage examples
├── main.py                       # Entry point
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy `env_example.txt` to `.env`:

   ```bash
   cp env_example.txt .env
   ```

2. Edit `.env` with your actual credentials:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key
   DATABASE_URL=postgresql://username:password@host:port/dbname
   ```

## Usage

### Basic Usage

Run the main application:

```bash
python main.py
```

### Programmatic Usage

```python
from src.core.sql_agent import SQLAgent

# Initialize the agent
agent = SQLAgent()

# Process a natural language query
result = agent.process_query("How many users signed up last month?")

if result["success"]:
    print(f"Generated SQL: {result['generated_sql']}")
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']}")

# Get database information
db_info = agent.get_database_info()
print(f"Available tables: {db_info['tables']}")

# Clean up
agent.close()
```

### Example Scripts

Run the example usage script:

```bash
python examples/basic_usage.py
```

### Running Tests

```bash
python -m unittest discover tests
```

## Key Components

### 1. SQLAgent (Core)

- Main orchestrator that coordinates all components
- Processes natural language queries end-to-end
- Provides database information and status

### 2. DatabaseManager

- Handles database connections
- Provides connection testing and cleanup
- Manages SQLAlchemy engine lifecycle

### 3. SchemaInspector

- Inspects database schema automatically
- Provides table names, column information
- Generates table summaries with row counts

### 4. SQLQueryGenerator

- Uses OpenAI LLM to generate SQL from natural language
- Includes database schema context for accuracy
- Validates generated SQL queries

### 5. Configuration

- Environment-based configuration management
- Validation of required settings
- Centralized configuration access

## Example Queries

- "How many applications did I get from 2023-01-01 to 2023-01-31?"
- "What is the total revenue for Q1 2023?"
- "Show me the top 10 customers by order value"
- "How many orders were placed yesterday?"

## Dependencies

- **langchain** - Core LangChain functionality
- **langchain-openai** - OpenAI integration
- **langchain-community** - Community utilities including SQL database
- **sqlalchemy** - Database ORM
- **psycopg2-binary** - PostgreSQL adapter
- **python-dotenv** - Environment variable management

## Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- Use strong database passwords
- Consider using connection pooling for production use

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Verify your DATABASE_URL format and credentials
2. **OpenAI API Error**: Check your API key and billing status
3. **Import Errors**: Ensure all dependencies are installed correctly
4. **Schema Inspection Errors**: Verify database permissions and table existence

### Getting Help

- Check the LangChain documentation: https://python.langchain.com/
- Verify your PostgreSQL connection separately
- Test your OpenAI API key independently
- Check the test files for usage examples

## Development

### Adding New Features

1. Create new modules in appropriate `src/` subdirectories
2. Add corresponding tests in `tests/`
3. Update this README with new functionality
4. Ensure all imports use relative paths within the package

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include docstrings for all public methods
- Write unit tests for new functionality
