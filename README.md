# Takehome Challenge

Build an **agentic chatbot** that can have conversations and use tools to accomplish tasks.

## The Challenge

This will only be for one user so don't worry about building a login flow, auth or security. Do however ensure the processes are async so that in theory if multiple users were on the platform it would not halt.

The purpose of this is for us to see you can set up agentic flows that a user can interact with. Additionally, we'd like to see that you can present this nicely through the frontend. For any clarification email: brandon@getstructured.ai.

### Requirements

#### 1. Conversation History
- The user should be able to chat with the bot
- Conversations should be persisted (use the SQLite database provided)
- The user should be able to view and return to previous conversations

#### 2. Tool Integration
The chatbot must be able to call the two tools defined in `backend/services/tools.py`:

- **Cat Fact** (`get_cat_fact`): Fetches a random cat fact from an external API
- **Calculator** (`calculate_expression`): Evaluates mathematical expressions

> **Tip:** Once the backend is running, visit **http://localhost:8000/docs** to explore the interactive API documentation. You can test both tool functions directly from the Swagger UI to understand how they work.

#### 3. Sequential Tool Calling
The chatbot should handle multi-step tasks that require calling tools in sequence. For example:

> "Get me a cat fact, count the number of words in the fact, and then use the calculator to divide that count by 7."

The bot should:
1. Call the cat fact tool to get a fact
2. Count the words in the returned fact
3. Call the calculator tool to divide the word count by 7
4. Return the final result to the user

All of this should happen in a single conversational turn.

### Notes

- You can use any LLM provider (OpenAI, Anthropic, etc.)
- Feel free to add any additional dependencies you need
- The backend already has SQLAlchemy set up with SQLite—use it for persistence
- Check `backend/services/tools.py` for the tool implementations

---

## Setup

### 1. Fork and Clone

```bash
# Fork this repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/takehome.git
cd takehome
```

### 2. Set Up Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Add your LLM API key(s) to `backend/.env`.

### 3. Install Dependencies

**Backend** (requires [uv](https://docs.astral.sh/uv/)):
```bash
cd backend
uv sync
```

**Frontend** (requires Node.js):
```bash
cd frontend
npm install
```

### 4. Run the Application

Start both servers in separate terminals:

**Backend** (runs on http://localhost:8000):
```bash
cd backend
uv run uvicorn main:app --reload
```

**Frontend** (runs on http://localhost:5173):
```bash
cd frontend
npm run dev
```
