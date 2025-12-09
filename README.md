# Structured Take-Home Challenge

**Build an agentic chatbot that can think, plan, and use tools.**

This exercise is intentionally scoped to be achievable within a few focused hours, but it touches the same patterns we use in production: **tool-using LLMs, async backend flows, clean persistence, and a polished user experience.**

---

## 🚀 What You’ll Build

A small **React + FastAPI** application where a user can chat with an AI assistant that:

* Remembers conversation history
* Uses a **set of tools** to accomplish tasks
* Can chain tools together in multi-step, reasoning-heavy sequences
* Presents everything cleanly on a modern frontend

You don’t need to build login, auth, or multi-tenant logic. Just focus on the core agentic workflow. All scaffolding for backend, frontend, and SQLite persistence is provided to make setup smooth.

If anything is unclear, feel free to reach out: **[brandon@getstructured.ai](mailto:brandon@getstructured.ai)**.

Because this is a simplified environment, assume only a single user will be using the system. Still, **make your backend async**, as if multiple requests *could* come in concurrently.

---

## 📌 Requirements

### 1. **Conversational Experience & Persistence**

Your chatbot should be able to:

* Chat naturally with the user
* Persist all messages to the provided SQLite database
* Display the list of previous conversations
* Allow the user to reopen and continue a past conversation

This mimics the baseline experience in our real product.

---

### 2. **Tool Integration**

Your agent must be able to use the two tool functions already implemented in
`backend/services/tools.py`:

* **Cat Fact Tool — `get_cat_fact()`**
  Fetches a random cat fact from an external API.

* **Calculator Tool — `calculate_expression()`**
  Evaluates a mathematical expression.

**Pro tip:**
Once your backend is running, visit **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI).
You can test both tools directly and understand the expected inputs and outputs.

---

### 3. **Sequential / Multi-Step Tool Calling**

Your agent should be able to handle tasks that require multiple tools in order.

Example prompt:

> “Get me a cat fact, count the number of words in it, and then use the calculator to divide that count by 7.”

Correct behavior:

1. Call the cat fact tool
2. Count the number of words
3. Call the calculator tool with the result
4. Return the final output to the user

All within a **single conversational turn**.
This is the kind of reasoning-layer orchestration we build internally every day.

---

## 🧠 Notes & Expectations

* You can use *any* LLM provider (OpenAI, Anthropic, etc.)
* Feel free to bring in additional dependencies if they help
* SQLAlchemy is already configured — please use it for persistence
* Tools for the challenge are in `backend/services/tools.py`
* Clean, readable code and a pleasant UI go a long way

---

# 🛠️ Setup Instructions

### 1. Fork & Clone the Repo

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/getstructured-ai/takehome.git
cd takehome
```

---

### 2. Configure Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Add the API keys provided in your email (OpenAI & Anthropic) to `backend/.env`.

If something is missing, just email **[brandon@getstructured.ai](mailto:brandon@getstructured.ai)**.

---

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

---

### 4. Run the App

Start backend & frontend in separate terminals.

**Backend** ([http://localhost:8000](http://localhost:8000)):

```bash
cd backend
uv run uvicorn main:app --reload
```

**Frontend** ([http://localhost:5173](http://localhost:5173)):

```bash
cd frontend
npm run dev
```

---

# 🎉 Final Thoughts

We designed this challenge to reflect real work you’d do at Structured:
agentic systems, tool orchestration, async Python, and thoughtful UI/UX.

Good luck, and have fun with it!
