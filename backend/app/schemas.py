from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Clue(BaseModel):
    id: str = Field(default_factory=lambda: f"clue_{uuid4().hex[:8]}")
    title: str
    detail: str
    scene_id: str
    points_to: list[str] = Field(default_factory=list)
    reliability: Literal["low", "medium", "high"] = "medium"


class Scene(BaseModel):
    id: str = Field(default_factory=lambda: f"scene_{uuid4().hex[:8]}")
    title: str
    character_name: str = ""
    description: str
    atmosphere: str
    clues: list[Clue] = Field(default_factory=list)


class PublicScene(BaseModel):
    id: str
    title: str
    character_name: str = ""
    description: str
    atmosphere: str


class Suspect(BaseModel):
    id: str = Field(default_factory=lambda: f"suspect_{uuid4().hex[:8]}")
    name: str
    role: str
    statement: str = ""
    motive: str
    alibi: str
    timeline: list[str]
    suspicious_detail: str


class PublicSuspect(BaseModel):
    id: str
    name: str
    role: str
    statement: str


class EvidenceLink(BaseModel):
    clue_id: str
    reasoning: str


class MysteryCase(BaseModel):
    id: str = Field(default_factory=lambda: f"case_{uuid4().hex[:12]}")
    title: str
    difficulty: Literal["easy", "medium", "high"] = "medium"
    crime_story: str
    victim: str
    case_type: str
    scenes: list[Scene]
    suspects: list[Suspect]
    accused_id: str
    timeline_summary: list[str]
    evidence_chain: list[EvidenceLink]
    red_herrings: list[str]
    verdict_reason: str
    validated: bool = False
    validation_notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CaseCreateRequest(BaseModel):
    difficulty: Literal["easy", "medium", "high"] = "medium"


class PublicMysteryCase(BaseModel):
    id: str
    title: str
    difficulty: str
    crime_story: str
    victim: str
    case_type: str
    scenes: list[PublicScene]
    suspects: list[PublicSuspect]
    timeline_summary: list[str]


class AccusationRequest(BaseModel):
    case_id: str
    suspect_id: str
    player_name: str | None = Field(default="Detective", max_length=40)


class AccusationResult(BaseModel):
    case_id: str
    selected_suspect_id: str
    correct_suspect_id: str
    is_correct: bool
    explanation: str
    evidence_chain: list[EvidenceLink]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    status: str
    database: str
    ai: str
