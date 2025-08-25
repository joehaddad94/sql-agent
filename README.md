# Natural Language SQL Agent

A powerful Natural Language to SQL agent built with **LangChain Platform**, OpenAI, and SQLAlchemy. This agent can understand natural language queries and convert them into SQL queries to interact with your database. Now using the modern LangChain Platform instead of the deprecated LangServe.

## Features

- 🧠 **Natural Language Understanding**: Convert plain English questions into SQL queries
- 🔧 **SQL Database Toolkit**: Built-in tools for querying, schema inspection, and validation
- 🚀 **ReAct Agent**: Uses LangChain's ReAct agent for intelligent query processing
- 📊 **Multiple Database Support**: Works with PostgreSQL, MySQL, SQLite, and more
- 🔒 **Safe Queries**: Prevents DML operations (INSERT, UPDATE, DELETE, DROP)
- 📈 **Streaming Support**: Real-time query processing with streaming output
- 🌐 **REST API**: FastAPI-based REST API with LangChain Platform integration
- 🛡️ **Error Handling**: Robust error handling and query validation
- 🔍 **LangSmith Integration**: Built-in tracing, monitoring, and debugging capabilities

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

# LangSmith Configuration (Optional - for tracing and monitoring)
# Get your API key from https://smith.langchain.com/
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=natural-language-sql-agent
LANGSMITH_TRACING_V2=true
```

### Supported Database URLs

- **PostgreSQL**: `postgresql://username:password@localhost:5432/mydb`
- **MySQL**: `mysql://username:password@localhost:3306/mydb`
- **SQLite**: `sqlite:///path/to/database.db`

## LangSmith Integration

This project includes comprehensive **LangSmith** integration for tracing, monitoring, and debugging your SQL agent interactions.

### What is LangSmith?

[LangSmith](https://smith.langchain.com/) is a platform for debugging, testing, evaluating, and monitoring LLM applications and chains. It provides:

- 🔍 **Trace Visualization**: See exactly how your agent processes queries
- 📊 **Performance Monitoring**: Track response times, costs, and success rates
- 🐛 **Debugging Tools**: Identify and fix issues in your agent logic
- 📈 **Analytics**: Understand usage patterns and optimize performance
- 🧪 **Testing Framework**: Test your agent with different inputs and scenarios

### Setting Up LangSmith

1. **Get an API Key**:
   - Visit [https://smith.langchain.com/](https://smith.langchain.com/)
   - Sign up for a free account
   - Generate an API key

2. **Configure Environment**:
   ```env
   LANGSMITH_API_KEY=your_api_key_here
   LANGSMITH_PROJECT=your_project_name
   ```

3. **Optional Settings**:
   ```env
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com  # Default
   LANGSMITH_TRACING_V2=true  # Enable V2 tracing
   ```

### Using LangSmith

#### Basic Usage

```python
from src.core.sql_agent import SQLAgent

# Initialize agent (LangSmith is automatically configured if API key is set)
agent = SQLAgent()

# Process queries with custom metadata
result = agent.process_query(
    "Show me the first 5 users",
    metadata={
        "user_id": "user_123",
        "session_id": "session_456",
        "query_category": "user_analysis",
        "tags": ["production", "user_query"]
    }
)

# Check LangSmith status
print(f"LangSmith enabled: {result['langsmith_enabled']}")
print(f"Project: {result['project']}")
```

#### API Usage with Metadata

```python
import requests

# Send request with LangSmith metadata
response = requests.post("http://localhost:8000/chat/invoke", json={
    "input": "How many applications were submitted this month?",
    "langsmith_metadata": {
        "user_id": "analyst_001",
        "session_id": "monthly_report_2024",
        "query_category": "monthly_analytics",
        "tags": ["monthly_report", "applications"],
        "custom_fields": {
            "report_type": "monthly",
            "priority": "high"
        }
    }
})

# Response includes LangSmith information
data = response.json()
print(f"LangSmith enabled: {data['langsmith_info']['enabled']}")
print(f"Project: {data['langsmith_info']['project']}")
```

#### Viewing Traces

1. **Visit LangSmith Dashboard**: [https://smith.langchain.com/](https://smith.langchain.com/)
2. **Navigate to Your Project**: Select the project specified in your configuration
3. **View Traces**: See detailed execution traces for each query
4. **Analyze Performance**: Monitor response times, costs, and success rates
5. **Debug Issues**: Step through the agent's decision-making process

### LangSmith Benefits

- **🔍 Complete Visibility**: See every step of query processing
- **📊 Performance Metrics**: Track costs, latency, and success rates
- **🐛 Easy Debugging**: Identify where queries fail or produce unexpected results
- **📈 Usage Analytics**: Understand how your agent is being used
- **🧪 Testing**: Compare different model versions and configurations
- **🔒 Security**: Monitor for suspicious or unexpected queries

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

### REST API Server

Start the FastAPI server with LangChain Platform integration:

```bash
python app.py
```

The server provides these endpoints:

- `GET /` - API information and available endpoints
- `GET /health` - Health check and database status
- `POST /chat/invoke` - Process natural language queries
- `POST /chat/stream` - Stream responses in real-time
- `POST /chat/batch` - Process multiple queries in batch
- `GET /docs` - Interactive API documentation

#### API Structure

The API is now organized in a clean, modular structure:

```
src/api/
├── models.py      # Request/response models with LangSmith support
├── routes/        # Endpoint handlers
│   ├── chat.py    # Chat endpoints with metadata support
│   ├── health.py  # Health checks
│   └── root.py    # API information
├── utils.py       # Helper functions
└── config.py      # App configuration
```

### Example Scripts

Run the basic usage example:

```bash
python examples/basic_usage.py
```

Run the LangSmith integration example:

```bash
python examples/langsmith_integration.py
```

Test LangSmith integration:

```bash
python test_langsmith.py
```

## How It Works

1. **Initialization**: The agent connects to your database and loads the SQL Database Toolkit
2. **LangSmith Setup**: If configured, LangSmith tracing is automatically enabled
3. **Query Processing**: Natural language queries are processed by the ReAct agent
4. **Tool Selection**: The agent automatically selects appropriate tools (query, schema, validation)
5. **SQL Generation**: Queries are converted to SQL and validated
6. **Execution**: Safe SQL queries are executed against your database
7. **Tracing**: All interactions are traced and sent to LangSmith (if enabled)
8. **Results**: Results are returned in a structured format with tracing information

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
- ✅ **LangSmith Monitoring**: Track and monitor all query activities

## Requirements

- Python 3.8+
- OpenAI API key
- Database connection
- Internet connection (for OpenAI API calls)
- LangSmith API key (optional, for tracing and monitoring)

## Dependencies

- **LangChain Platform**: Modern framework for LLM applications (replaces deprecated LangServe)
- **LangGraph**: Agent orchestration and execution
- **LangSmith**: Tracing, monitoring, and debugging platform
- **OpenAI**: Language model integration
- **SQLAlchemy**: Database abstraction layer
- **psycopg2**: PostgreSQL adapter
- **FastAPI**: High-performance web framework for building APIs

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your `.env` file has the correct API key
2. **Database Connection Error**: Verify your database URL and credentials
3. **Package Installation Issues**: Try updating pip: `pip install --upgrade pip`
4. **LangSmith Connection Issues**: Verify your LangSmith API key and endpoint

### LangSmith Troubleshooting

1. **No Traces Appearing**:
   - Check your `LANGSMITH_API_KEY` is set correctly
   - Verify the API key has proper permissions
   - Check network connectivity to `api.smith.langchain.com`

2. **Traces in Wrong Project**:
   - Set `LANGSMITH_PROJECT` to your desired project name
   - Ensure the project exists in your LangSmith account

3. **Performance Issues**:
   - LangSmith adds minimal overhead (< 100ms typically)
   - Disable tracing by setting `LANGSMITH_TRACING_V2=false` if needed

### Getting Help

If you encounter issues:

1. Check your environment variables
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Check LangSmith configuration
5. Check the error messages for specific guidance

## Migration from LangServe

This project has been migrated from the deprecated **LangServe** to the modern **LangChain Platform**. The key changes include:

- ✅ **Removed LangServe dependencies** - No more `langserve` or `sse_starlette` packages
- ✅ **Standard FastAPI endpoints** - Clean, maintainable REST API implementation
- ✅ **Enhanced functionality** - Added streaming, batch processing, and better error handling
- ✅ **LangSmith Integration** - Built-in tracing and monitoring capabilities
- ✅ **Future-proof** - Uses the actively maintained LangChain Platform

### What Changed

- **Before**: Used `langserve.add_routes()` for automatic endpoint generation
- **After**: Custom FastAPI endpoints with full control over request/response handling
- **Benefits**: Better performance, more flexibility, easier debugging, and comprehensive monitoring

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
