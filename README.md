# ClueHunt

ClueHunt is an AI-powered mystery-solving game. Players generate a unique case, inspect scenes, clues, suspects, timelines, and red herrings, then submit a final accusation. The backend uses a LangGraph workflow with separate AI responsibilities for case generation, logic validation, and verdict explanation.

## Stack

- Frontend: React, Vite, Tailwind CSS
- Backend: FastAPI, Python
- AI orchestration: LangGraph
- LLM provider: Groq
- Database: MongoDB with in-memory fallback
- Optional memory extension: ChromaDB or FAISS can be added to compare new case embeddings against previous mysteries

## Project Structure

```text
backend/
  app/
    ai_workflow.py   LangGraph agents and fallback case generation
    db.py            MongoDB persistence with memory fallback
    main.py          FastAPI routes
    schemas.py       Shared API and AI data models
    settings.py      Environment configuration
frontend/
  src/
    components/      Game UI sections
    api.js           API client
    App.jsx          Game state and flow
```

## Environment

Create `.env` at the repository root:

```bash
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/Clue_Hunt
DATABASE_NAME=Clue_Hunt
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GROQ_MODEL=llama-3.1-70b-versatile
```

The app still works without Groq or MongoDB by using a deterministic fallback case and in-memory storage.

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs will be available at `http://localhost:8000/docs`.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API

- `GET /health` checks API, AI mode, and database mode.
- `POST /api/cases` creates a public mystery case with a random theme.
- `GET /api/cases/{case_id}` retrieves a public case file.
- `POST /api/accuse` evaluates the selected suspect and returns the verdict explanation.

## AI Workflow

1. Case Generator Agent creates the crime story, scenes, suspects, motives, timelines, clues, red herrings, accused suspect, and evidence chain.
2. Logic Validator Agent checks whether the accused, clues, and timeline references are structurally consistent, then asks the LLM for a consistency review when available.
3. Explanation Agent evaluates the submitted accusation and produces a detective-style verdict explanation based on evidence and timeline.
