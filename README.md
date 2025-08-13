# Natural Language SQL Agent

A powerful Natural Language to SQL agent built with LangChain, OpenAI, and SQLAlchemy. This agent can understand natural language queries and convert them into SQL queries to interact with your database.

## Features

- 🧠 **Natural Language Understanding**: Convert plain English questions into SQL queries
- 🔧 **SQL Database Toolkit**: Built-in tools for querying, schema inspection, and validation
- 🚀 **ReAct Agent**: Uses LangChain's ReAct agent for intelligent query processing
- 📊 **Multiple Database Support**: Works with PostgreSQL, MySQL, SQLite, and more
- 🔒 **Safe Queries**: Prevents DML operations (INSERT, UPDATE, DELETE, DROP)
- 📈 **Streaming Support**: Real-time query processing with streaming output
- 🛡️ **Error Handling**: Robust error handling and query validation

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Natural-Language-SQL-Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   # Edit .env with your actual values
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Optional Configuration
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.0
```

### Supported Database URLs

- **PostgreSQL**: `postgresql://username:password@localhost:5432/mydb`
- **MySQL**: `mysql://username:password@localhost:3306/mydb`
- **SQLite**: `sqlite:///path/to/database.db`

## Usage

### Basic Usage

```python
from src.core.sql_agent import SQLAgent

# Initialize the agent
agent = SQLAgent()

# Process a natural language query
result = agent.process_query("Show me the first 5 users")
print(result)

# Clean up
agent.close()
```

### Interactive Mode

Run the main script for an interactive experience:

```bash
python main.py
```

### Example Scripts

Run the basic usage example:

```bash
python examples/basic_usage.py
```

## How It Works

1. **Initialization**: The agent connects to your database and loads the SQL Database Toolkit
2. **Query Processing**: Natural language queries are processed by the ReAct agent
3. **Tool Selection**: The agent automatically selects appropriate tools (query, schema, validation)
4. **SQL Generation**: Queries are converted to SQL and validated
5. **Execution**: Safe SQL queries are executed against your database
6. **Results**: Results are returned in a structured format

## Available Tools

The SQL Database Toolkit provides these tools:

- **QuerySQLDatabaseTool**: Execute SQL queries and return results
- **InfoSQLDatabaseTool**: Get schema and sample data for tables
- **ListSQLDatabaseTool**: List all available tables
- **QuerySQLCheckerTool**: Validate SQL queries before execution

## Safety Features

- ❌ **No DML Operations**: INSERT, UPDATE, DELETE, DROP are blocked
- ✅ **Query Validation**: All queries are validated before execution
- ✅ **Schema Inspection**: Automatic table and column validation
- ✅ **Error Handling**: Comprehensive error handling and recovery

## Requirements

- Python 3.8+
- OpenAI API key
- Database connection
- Internet connection (for OpenAI API calls)

## Dependencies

- **LangChain**: Core framework for LLM applications
- **LangGraph**: Agent orchestration and execution
- **OpenAI**: Language model integration
- **SQLAlchemy**: Database abstraction layer
- **psycopg2**: PostgreSQL adapter

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your `.env` file has the correct API key
2. **Database Connection Error**: Verify your database URL and credentials
3. **Package Installation Issues**: Try updating pip: `pip install --upgrade pip`

### Getting Help

If you encounter issues:

1. Check your environment variables
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Check the error messages for specific guidance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
