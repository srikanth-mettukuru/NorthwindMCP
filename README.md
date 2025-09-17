# NorthwindMCP

A **Model Context Protocol (MCP) Server** implementation for the Northwind database with an AI-powered Streamlit chatbot interface.

## 🌟 Overview

This project demonstrates a modern AI-powered database assistant built with:
- **MCP Server**: Exposes specialized database tools and operations
- **AI Agent**: Uses LangChain + OpenAI to understand natural language queries
- **Streamlit App**: Interactive web interface for database conversations
- **PostgreSQL**: Northwind sample database hosted on AWS RDS



### 🛠️ **MCP Server Tools**
- **`get_tables`**: Discover available database tables
- **`get_columns`**: Inspect table structures and column information
- **`query`**: Execute custom SQL queries with safety checks
- **`sales_report`**: Generate comprehensive sales analytics with optional date filtering
- **`customer_orders`**: Analyze customer ordering patterns and history



## 📁 Project Structure

```
NorthwindMCP/
├── northwind-mcp-server/          # MCP Server Implementation
│   ├── main.py                    # FastMCP server entry point
│   ├── service.py                 # Business logic and tool implementations
│   ├── database.py                # PostgreSQL connection and query execution
│   ├── unittests.py               # Database layer tests
│   ├── requirements.txt           # Server dependencies
│   └── .env.example               # Example Server configuration
├── northwind-mcp-client/          # MCP Client & AI Agent
│   ├── mcp_client.py              # MCP protocol client implementation
│   ├── agent.py                   # LangChain agent with OpenAI integration
│   ├── agent_tests.py             # End-to-end agent tests
│   ├── requirements.txt           # Client dependencies
│   └── .env.example               # Example Client configuration
└── streamlit-app/                 # Web Application
    ├── app.py                     # Streamlit interface
    ├── requirements.txt           # Combined dependencies for deployment
    └── .env.example               # Example Deployment configuration
```


## 🔧 Technology Stack

- **Backend**: FastMCP, PostgreSQL, psycopg2
- **AI/ML**: LangChain, OpenAI GPT-4.1-mini
- **Frontend**: Streamlit
- **Protocol**: Model Context Protocol (MCP)
- **Testing**: pytest
- **Deployment**: Streamlit Cloud


## 📝 Usage
This project is created for educational and learning purposes.