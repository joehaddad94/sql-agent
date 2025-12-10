# API Structure Documentation

This directory contains the refactored API structure for the Natural Language SQL Agent.

## 📁 Directory Structure

```
src/api/
├── __init__.py          # API module initialization
├── models.py            # Pydantic models for requests/responses
├── utils.py             # Utility functions (e.g., extract_clean_answer)
├── config.py            # FastAPI app configuration
├── router.py            # Main router registry
├── routes/              # Individual route modules
│   ├── __init__.py      # Routes module initialization
│   ├── chat.py          # Chat endpoints (/chat/*)
│   ├── health.py        # Health check endpoint (/health)
│   └── root.py          # Root endpoint (/)
└── README.md            # This file
```

## 🏗️ Architecture Overview

### **Separation of Concerns**

- **Models**: Data validation and serialization
- **Routes**: Endpoint logic and handlers
- **Utils**: Helper functions and utilities
- **Config**: Application setup and configuration
- **Router**: Route registration and management

### **Benefits of This Structure**

1. **Maintainability**: Each component has a single responsibility
2. **Readability**: Easy to find and understand specific functionality
3. **Testability**: Individual components can be tested in isolation
4. **Scalability**: Easy to add new endpoints and features
5. **Reusability**: Components can be reused across different parts of the app

## 🔧 How It Works

### **1. App Creation (`config.py`)**

```python
def create_app() -> FastAPI:
    app = FastAPI(title="...", description="...", version="...")
    api_router = create_api_router()
    app.include_router(api_router)
    return app
```

### **2. Route Registration (`router.py`)**

```python
def create_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(root.router)
    api_router.include_router(health.router)
    api_router.include_router(chat.router)
    return api_router
```

### **3. Individual Routes (`routes/*.py`)**

Each route module defines its own router with specific endpoints:

```python
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/invoke")
async def chat_invoke(request: ChatInput):
    # Endpoint logic here
```

## 📍 Available Endpoints

| Endpoint       | Method | Description      | File               |
| -------------- | ------ | ---------------- | ------------------ |
| `/`            | GET    | API information  | `routes/root.py`   |
| `/health`      | GET    | Health check     | `routes/health.py` |
| `/chat/invoke` | POST   | Process query    | `routes/chat.py`   |
| `/chat/stream` | POST   | Stream response  | `routes/chat.py`   |
| `/chat/batch`  | POST   | Batch processing | `routes/chat.py`   |

## 🚀 Adding New Endpoints

### **1. Create a new route file**

```python
# src/api/routes/new_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/new-feature", tags=["new-feature"])

@router.get("/")
async def new_endpoint():
    return {"message": "New feature!"}
```

### **2. Register the route**

```python
# src/api/router.py
from src.api.routes import new_feature

def create_api_router() -> APIRouter:
    api_router = APIRouter()
    # ... existing routes ...
    api_router.include_router(new_feature.router)
    return api_router
```

## 🧪 Testing

Use the test script to verify the refactored structure:

```bash
python test_refactored_api.py
```

## 🔄 Migration Notes

This structure replaces the previous monolithic `app.py` file with:

- ✅ **Cleaner separation** of concerns
- ✅ **Easier maintenance** and debugging
- ✅ **Better organization** of code
- ✅ **Improved readability** and structure
- ✅ **Easier testing** of individual components

## 📚 Dependencies

- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **SQLAgent**: Core business logic
- **Config**: Configuration management
