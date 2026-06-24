import asyncio
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ai_workflow import build_case_workflow, build_explanation_workflow
from app.db import MongoStore
from app.schemas import (
    AccusationRequest,
    AccusationResult,
    CaseCreateRequest,
    HealthResponse,
    MysteryCase,
    PublicMysteryCase,
    PublicScene,
    PublicSuspect,
)
from app.settings import get_settings


settings = get_settings()
store = MongoStore(settings)
case_workflow = build_case_workflow(settings)
explanation_workflow = build_explanation_workflow(settings)
memory_cases: dict[str, dict] = {}


def groq_status() -> str:
    disabled_ai_keys = {"", "fallback", "disabled", "none"}
    if (settings.groq_api_key or "").lower() in disabled_ai_keys:
        return "fallback"
    return "groq"


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider = groq_status()
    if provider == "groq":
        print(f"[ClueHunt AI] Groq enabled. Model: {settings.groq_model}", flush=True)
    else:
        print("[ClueHunt AI] Groq disabled or missing. Using fallback case generator.", flush=True)
    try:
        await store.connect()
    except Exception:
        pass
    yield
    await store.close()


app = FastAPI(title="ClueHunt AI Mystery API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def public_statement(suspect) -> str:
    if suspect.statement and suspect.statement.strip():
        return suspect.statement.strip()
    if suspect.alibi and suspect.alibi.strip():
        return suspect.alibi.strip()
    if suspect.timeline:
        return f"I can account for my movements: {'; '.join(suspect.timeline)}. That is all I know."
    return "I told the investigators where I was. Someone is twisting the timing to make me look guilty."


def public_case(case: MysteryCase) -> PublicMysteryCase:
    suspects = list(case.suspects)
    random.shuffle(suspects)
    public_scenes = [
        PublicScene(
            id=scene.id,
            title=scene.title,
            character_name=scene.character_name,
            description=scene.description,
            atmosphere=scene.atmosphere,
        )
        for scene in case.scenes
    ]
    public_suspects = [
        PublicSuspect(id=suspect.id, name=suspect.name, role=suspect.role, statement=public_statement(suspect))
        for suspect in suspects
    ]
    return PublicMysteryCase(
        id=case.id,
        title=case.title,
        difficulty=case.difficulty,
        crime_story=case.crime_story,
        victim=case.victim,
        case_type=case.case_type,
        scenes=public_scenes,
        suspects=public_suspects,
        timeline_summary=case.timeline_summary,
    )


async def load_case(case_id: str) -> MysteryCase | None:
    doc = await store.get_case(case_id)
    if doc is None:
        doc = memory_cases.get(case_id)
    if doc is None:
        return None
    return MysteryCase.model_validate(doc)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    database = "connected" if store.db is not None else "memory"
    return HealthResponse(status="ok", database=database, ai=groq_status())


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "ClueHunt AI Mystery API",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/api/cases", response_model=PublicMysteryCase)
async def create_case(request: CaseCreateRequest) -> PublicMysteryCase:
    recent = await store.recent_cases()
    recent_summaries = [f"{doc.get('title')}: {doc.get('crime_story')}" for doc in recent]
    state = await asyncio.to_thread(
        case_workflow.invoke,
        {"request": request, "recent_case_summaries": recent_summaries},
    )
    case = state["case"]
    provider = state.get("ai_provider", groq_status())
    print(f"[ClueHunt AI] Case generated with: {provider}. Title: {case.title}", flush=True)
    if state.get("error"):
        print(f"[ClueHunt AI] Groq generation failed, fallback used. Error: {state['error']}", flush=True)
    doc = case.model_dump(mode="json")
    memory_cases[case.id] = doc
    await store.save_case(doc)
    return public_case(case)


@app.get("/api/cases/{case_id}", response_model=PublicMysteryCase)
async def get_case(case_id: str) -> PublicMysteryCase:
    case = await load_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return public_case(case)


@app.post("/api/accuse", response_model=AccusationResult)
async def accuse(request: AccusationRequest) -> AccusationResult:
    case = await load_case(request.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if request.suspect_id not in {suspect.id for suspect in case.suspects}:
        raise HTTPException(status_code=400, detail="Unknown suspect")

    state = await asyncio.to_thread(
        explanation_workflow.invoke,
        {
            "case": case,
            "selected_suspect_id": request.suspect_id,
            "player_name": request.player_name or "Detective",
        },
    )
    result = state["result"]
    await store.save_history(result.model_dump(mode="json"))
    return result
