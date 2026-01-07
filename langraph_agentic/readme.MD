# Agentic Call Center - Production POC

A production-grade Agentic AI Call Center system built with LangGraph, FastAPI, and Docker. This system implements a hierarchical multi-agent architecture for handling customer service queries across Claims, Billing, and Scheduling domains.

## 🏗 Architecture

### System Design

```
User Query
    ↓
Orchestrator Agent (Routes to domain agent)
    ↓
Domain Agent (Claims | Billing | Scheduling)
    ↓
Safety Sentinel (Validates response)
    ↓
Response to User
```

### Key Components

1. **Orchestrator Agent**: Routes queries to appropriate domain agents (never calls tools directly)
2. **Domain Agents**: 
   - **Claims Agent**: Handles insurance claims, claim status, coverage questions
   - **Billing Agent**: Handles billing, payments, account balances
   - **Scheduling Agent**: Handles appointments, rescheduling, cancellations
3. **Safety Sentinel**: Validates all responses before returning to users (human-in-the-loop flagging)
4. **Memory System**: Vector store for conversation context and summarization
5. **Tools**: Mock MCP-style tools for backend operations

### Architecture Principles

- **Hierarchical Multi-Agent**: Orchestrator → Domain Agent → Sentinel
- **Shared Blackboard**: All agents read/write to GraphState (Pydantic TypedDict)
- **No Direct Tool Calls from Orchestrator**: Orchestrator only routes, never executes tools
- **Safety First**: All responses validated by Safety Sentinel
- **Cyclic Reasoning**: LangGraph supports cyclic workflows for complex reasoning

## 📁 Project Structure

```
agentic-call-center/
│
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── graph.py                # LangGraph definition
│   ├── state.py                # Blackboard schema (GraphState)
│
├── agents/
│   ├── orchestrator.py         # Orchestrator agent (routing only)
│   ├── claims/
│   │   ├── agent.py            # Claims domain agent
│   │   ├── tools.py            # Claims tools
│   │   └── prompt.py           # Claims agent prompt
│   ├── billing/
│   │   ├── agent.py            # Billing domain agent
│   │   ├── tools.py            # Billing tools
│   │   └── prompt.py           # Billing agent prompt
│   ├── scheduling/
│   │   ├── agent.py            # Scheduling domain agent
│   │   ├── tools.py            # Scheduling tools
│   │   └── prompt.py           # Scheduling agent prompt
│
├── safety/
│   ├── sentinel.py             # Safety validation agent
│   └── antifraud.py            # Anti-fraud detection
│
├── memory/
│   ├── vector_store.py         # Vector store for conversation memory
│   └── summarizer.py           # Conversation summarization
│
├── tools/
│   ├── mcp_registry.py         # MCP tool registry
│   └── mock_backend.py         # Mock backend services
│
├── infra/
│   ├── Dockerfile              # Docker image definition
│   └── docker-compose.yml      # Docker Compose configuration
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Groq API key (get it from https://console.groq.com/)

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd classroom-customer-service-agentic-google-adk-phase-2-/langraph_agentic
   ```

2. **Create `.env` file**:
   Copy the example file and add your API key:
   ```bash
   cp env.example .env
   ```
   
   Then edit `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-70b-versatile
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   VECTOR_STORE_PATH=./chroma_db
   LOG_LEVEL=INFO
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose -f infra/docker-compose.yml up --build
   ```
   
   The docker-compose.yml will automatically load environment variables from the `.env` file.

4. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the status of claim CLM-12345?"}'
   ```

### Running Locally (Without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Groq API key. The application will automatically load variables from `.env` using python-dotenv.

3. **Run the application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📡 API Endpoints

### `POST /chat`

Main chat endpoint for processing user queries.

**Request**:
```json
{
  "message": "What is the status of my claim?",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "response": "Your claim CLM-12345 is approved for $5,000.00...",
  "agent": "claims",
  "requires_human_review": false,
  "safety_flags": [],
  "risk_score": 0.0,
  "session_id": "session-id",
  "routing_info": {
    "next_agent": "claims",
    "routing_confidence": 0.9,
    "routing_reasoning": "LLM routed to claims based on query intent"
  }
}
```

### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "graph_initialized": true
}
```

## 🔧 Configuration

### Environment Variables

All configuration is done through a `.env` file in the project root. Copy `env.example` to `.env` and update the values:

- `GROQ_API_KEY`: **Required**. Your Groq API key (get it from https://console.groq.com/).
- `GROQ_MODEL`: Optional. Default: `llama-3.1-70b-versatile`. Available models:
  - `llama-3.1-70b-versatile` (recommended, best quality)
  - `llama-3.1-8b-instant` (faster, lower cost)
  - `mixtral-8x7b-32768` (long context)
  - `gemma2-9b-it` (alternative option)
- `EMBEDDING_MODEL`: Optional. Default: `sentence-transformers/all-MiniLM-L6-v2` (local embeddings, no API key needed)
- `VECTOR_STORE_PATH`: Optional. Default: `./chroma_db`
- `LOG_LEVEL`: Optional. Default: `INFO`

**Note**: 
- When using Docker Compose, the `.env` file is automatically loaded via `env_file` in docker-compose.yml
- When running locally, the application loads `.env` using `python-dotenv` in `app/main.py`
- Never commit your `.env` file to version control (it's in .gitignore)

## 🛡️ Safety Features

### Safety Sentinel

The Safety Sentinel validates all agent responses before returning to users:

- **Accuracy checks**: Validates information correctness
- **Appropriateness checks**: Ensures appropriate tone and content
- **Security checks**: Flags sensitive information
- **Compliance checks**: Ensures regulatory compliance
- **Human-in-the-loop**: Flags responses requiring human review

### Anti-Fraud Detection

The anti-fraud module detects:
- Fraud patterns in queries
- Suspicious keywords
- Unusual payment methods
- Multiple urgent requests

## 🧠 Memory System

### Vector Store

- Stores conversation history with semantic search
- Retrieves relevant context from past conversations
- Uses ChromaDB for persistence

### Conversation Summarization

- Summarizes long conversation histories
- Maintains context window efficiency
- Preserves key information and decisions

## 🧪 Testing

### Example Queries

**Claims**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the status of claim CLM-12345?"}'
```

**Billing**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my account balance for ACC-12345?"}'
```

**Scheduling**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I schedule an appointment for next week?"}'
```

## 📝 Implementation Notes

### Design Decisions

1. **Orchestrator Never Calls Tools**: The orchestrator only routes queries. All tool execution happens in domain agents.

2. **Shared Blackboard Pattern**: All agents read from and write to `GraphState`, enabling information sharing.

3. **Mock Tools**: All tools are mock implementations for POC purposes. In production, these would connect to real backend services.

4. **Safety First**: Every response goes through the Safety Sentinel before being returned to users.

5. **LangGraph for Control Flow**: LangGraph provides explicit control flow and state management, making the system easier to debug and maintain.

### Extensibility

- **Add New Domain Agents**: Create a new agent in `agents/` following the existing pattern
- **Add New Tools**: Register tools in the MCP registry or add to domain agent tools
- **Customize Safety Rules**: Modify `safety/sentinel.py` for custom validation logic
- **Add Memory Features**: Extend `memory/vector_store.py` for additional memory capabilities

## 🐛 Troubleshooting

### Common Issues

1. **Groq API Key Error**: 
   - Ensure you have created a `.env` file from `env.example`
   - Verify `GROQ_API_KEY` is set correctly in your `.env` file
   - Get your API key from https://console.groq.com/
   - For Docker: Ensure the `.env` file is in the project root (same directory as docker-compose.yml's parent)
   - For local: The app loads `.env` automatically via python-dotenv

2. **Port Already in Use**: Change the port in `docker-compose.yml` or stop the conflicting service.

3. **Import Errors / Version Mismatch**: 
   - If you see `ModuleNotFoundError: No module named 'langchain_core.pydantic_v1'`:
     ```bash
     # Uninstall old versions first
     pip uninstall -y langchain langchain-openai langchain-community langchain-core langgraph
     
     # Reinstall with correct versions
     pip install -r requirements.txt
     
     # Or force reinstall
     pip install --upgrade --force-reinstall -r requirements.txt
     ```
   - On Windows PowerShell, you can also run: `.\install_dependencies.ps1`

4. **ChromaDB Errors**: The vector store will be created automatically. Ensure write permissions in the `chroma_db` directory.

## 📚 Dependencies

- **FastAPI**: Web framework
- **LangGraph**: Agent orchestration
- **LangChain**: LLM integration
- **Groq**: LLM provider (fast inference)
- **ChromaDB**: Vector store
- **Sentence Transformers**: Local embeddings (no API key needed)
- **Pydantic**: Data validation

## 🔮 Future Enhancements

- [ ] Real backend API integrations
- [ ] Advanced fraud detection with ML models
- [ ] Multi-language support
- [ ] Voice interface integration
- [ ] Real-time streaming responses
- [ ] Advanced conversation analytics
- [ ] A/B testing framework for agents
- [ ] Performance monitoring and observability

## 📄 License

This is a POC project for demonstration purposes.

## 👥 Contributing

This is a production POC. For production use, consider:
- Adding comprehensive test coverage
- Implementing proper error handling and retries
- Adding monitoring and observability
- Implementing rate limiting
- Adding authentication and authorization
- Implementing proper logging and audit trails

---

**Built with ❤️ using LangGraph, FastAPI, and Docker**
