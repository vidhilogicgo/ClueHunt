# ClueHunt Architecture & Documentation

Welcome to the ClueHunt Documentation! This guide provides a comprehensive overview of the architecture, data flow, AI workflows, and project structure for the ClueHunt mystery-solving game.

## 1. Product Overview

ClueHunt is an AI-powered interactive mystery game. Players are presented with dynamically generated cases, complete with crime scenes, character statements, timelines, and clues. The goal is to interrogate the suspects' statements, cross-reference them with scene evidence, and identify the single suspect who is lying to crack the case.

**Key Features:**
- **Dynamic Case Generation:** Every round features a unique story, generated on-the-fly by an LLM or using a robust deterministic fallback.
- **Logic Validation:** An AI validator ensures that the generated mystery is structurally sound and that only one suspect is definitively lying.
- **Verdict Explanation:** Upon accusing a suspect, an LLM acts as a detective to explain the verdict based on the evidence chain.

## 2. Technology Stack

- **Frontend:** React, Vite, Tailwind CSS, Lucide Icons
- **Backend:** Python, FastAPI, Pydantic
- **AI Orchestration:** LangGraph, LangChain
- **LLM Provider:** Groq (`llama-3.1-70b-versatile` by default)
- **Database (Optional):** MongoDB (with in-memory fallback)

---

## 3. System Architecture

The application is split into two primary layers: a React Single Page Application (SPA) on the frontend, and a FastAPI service on the backend orchestrating LangGraph workflows.

### 3.1 Backend & AI Workflows
The backend lives in the `backend/` directory. The AI logic is structured using **LangGraph**, which handles multi-agent state machines to generate and validate the cases.

#### **Case Generation Workflow (`CaseWorkflowState`)**
1. **`case_generator` Node:** 
   - Prompts the LLM (Groq) with a highly specific instruction set to invent a fresh, high-stakes mystery (e.g., jewel theft, poisoning, espionage).
   - Validates the output schema using Pydantic.
   - Enforces subtlety by checking for forbidden "giveaway" phrases in the public-facing text.
   - **Fallback:** If the LLM fails or no API key is provided, a complex deterministic fallback case is used.
2. **`logic_validator` Node:**
   - Evaluates the generated case to ensure structural consistency.
   - Verifies that exactly one suspect's statement is false, and that the evidence chain properly links clues to the guilty party without relying on cheap chronological tricks.

#### **Verdict Explanation Workflow (`ExplanationState`)**
- **`explanation_agent` Node:** 
  - Takes the player's accusation and the original case data.
  - Determines if the player is correct.
  - Generates a "detective-style" explanation summarizing the evidence chain, why the accused is guilty, and why the innocent suspects were red herrings.

### 3.2 Frontend Architecture
The frontend is a Vite-powered React application (`frontend/`). 
It features a modular component structure:
- **`CaseSetup.jsx`**: Landing area to start a new investigation and choose difficulty.
- **`CaseFile.jsx` / `InvestigationBoard.jsx`**: Renders the crime scenes, suspect profiles, and clues.
- **`AccusationPanel.jsx`**: The bottom sticky bar where the player submits their final verdict.
- **`VerdictModal.jsx`**: A modal that pops up displaying the result and the `explanation_agent`'s breakdown.

---

## 4. API Reference

The FastAPI backend exposes the following primary endpoints:

- `GET /health`
  - Returns the health status, active AI provider (Groq or Fallback), and active database mode.
- `POST /api/cases`
  - Triggers the LangGraph `case_generator` workflow and returns a full `MysteryCase` object.
- `GET /api/cases/{case_id}`
  - Fetches a specific case from the database (or in-memory store).
- `POST /api/accuse`
  - Accepts a `case_id` and the player's `selected_suspect_id`.
  - Triggers the LangGraph `explanation_agent` and returns the `AccusationResult`.

---

## 5. Local Setup & Development

### Prerequisites
- Node.js & npm
- Python 3.10+

### Backend Setup
```bash
cd backend
python -m venv .venv
# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GROQ_MODEL=llama-3.1-70b-versatile
```
Run the backend:
```bash
uvicorn app.main:app --reload
# Available at http://localhost:8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:5173
```

## 6. Project Directory Structure
```text
ClueHunt/
├── backend/
│   ├── app/
│   │   ├── ai_workflow.py    # LangGraph definitions
│   │   ├── db.py             # MongoDB / InMemory persistence
│   │   ├── main.py           # FastAPI application
│   │   ├── schemas.py        # Pydantic models
│   │   └── settings.py       # Env vars configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # UI Components
│   │   ├── App.jsx           # Main App State
│   │   ├── api.js            # Fetch wrappers
│   │   ├── main.jsx          # React entry point
│   │   └── styles.css        # Tailwind directives
│   ├── package.json
│   ├── postcss.config.js
│   └── tailwind.config.js
├── README.md                 # Brief introduction
├── DOCUMENTATION.md          # This file
└── .env.example              # Environment variable template
```
