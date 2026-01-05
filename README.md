# Mission Control - Take-Home Challenge

Anthropic's recently released Programmatic Tool Calling (PTC) is quite powerful.
You're goal is to utilize this new tool to build an AI Operations Assistant.

---

## Requirements

### 1. Implement Programmatic Tool Calling

Connect the chat to Claude with PTC enabled. When Claude writes code that calls tools in its secure environment, respond to those tool calls from your backend and return results back to Claude's code execution.

See `backend/services/tools.py` for 3 starter tools with `allowed_callers` already configured.

**Docs:** [Programmatic Tool Calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)

### 2. Real-Time Visualization

Stream tool execution to the frontend. Users should see:

- When Claude writes code vs calls tools directly
- If Claude writes code we should see this code
- Each tool call as it happens (not after completion)
- Intermediate results and the final response

You don't have to stream individual tokens (though bonus if you can). The idea here is that the user should see what's happening as the agent thinks rather than waiting a few minutes to receive a massive chunk of text.

### 3. Conversation Context

The agent should handle follow-up questions correctly. If I ask "List P0 incidents" then follow up with "Who's assigned to the first one?", the agent should understand the context.

### 4. Chat History

- Create new conversations
- Return to previous conversations
- Persist messages to the database (SQLite + SQLAlchemy already configured)

### 5. Build Tools to Answer These Questions

Your agent should correctly answer all of these:

| Question                                                          | Hints                        |
| ----------------------------------------------------------------- | ---------------------------- |
| "Which departments are over budget?"                              | Need budget data             |
| "What projects have declining customer satisfaction?"             | Need feedback/NPS data       |
| "List engineers with unresolved P1+ incidents and their managers" | Correlate team + incidents   |
| "Which project has the worst incident-to-deployment ratio?"       | Need deployment data         |
| "Create a summary of infrastructure issues this month"            | Filter + aggregate incidents |

Look at `backend/data/mock_data.py` - there's data for budgets, customer feedback, and deployments that don't have tools yet. **You decide what tools to build.**

---

## Getting Started

```bash
# Backend
cd backend
cp .env.example .env  # Add your Anthropic API key from Structured AI
uv sync
uv run uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

## Submission

**[Schedule Review Call](https://calendly.com/brandon-getstructured/60-minute-meeting)**

Questions? Email **brandon@getstructured.ai**
