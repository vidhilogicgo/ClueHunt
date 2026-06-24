import json
import random
from uuid import uuid4
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import ValidationError

from app.schemas import AccusationResult, CaseCreateRequest, MysteryCase
from app.settings import Settings


CASE_THEMES = [
    {
        "name": "rain-soaked museum gala",
        "case_type": "jewel theft",
        "object": "Maharaja's blue diamond necklace",
        "victim_role": "museum curator",
        "incident": "the necklace vanished from its sealed glass case during a staged power cut",
        "hook": "The display case was locked again before anyone noticed the jewel was gone.",
        "locations": ["Gem Gallery", "Security Corridor", "Donation Hall"],
    },
    {
        "name": "midnight observatory",
        "case_type": "attempted murder",
        "object": "poisoned thermos",
        "victim_role": "lead astronomer",
        "incident": "the lead astronomer collapsed after drinking from a thermos kept beside the telescope controls",
        "hook": "The poison was added during a two-minute blackout, but the cup was wiped too carefully.",
        "locations": ["Telescope Deck", "Control Room", "Glass Walkway"],
    },
    {
        "name": "heritage hotel banquet",
        "case_type": "murder",
        "object": "rare saffron poison",
        "victim_role": "celebrity chef",
        "incident": "the celebrity chef died after tasting the final course before a royal dinner",
        "hook": "Everyone saw the dish being plated, but one garnish tray changed hands in the rush.",
        "locations": ["Pastry Kitchen", "Cold Pantry", "Banquet Hall"],
    },
    {
        "name": "private bank vault",
        "case_type": "gold theft",
        "object": "antique gold idol",
        "victim_role": "vault manager",
        "incident": "an antique gold idol disappeared from a private vault during a private appraisal",
        "hook": "The vault door never showed a forced entry, but the weight sensor dipped twice.",
        "locations": ["Vault Room", "Counting Desk", "Client Lounge"],
    },
    {
        "name": "startup launch party",
        "case_type": "prototype theft",
        "object": "quantum payment chip",
        "victim_role": "product founder",
        "incident": "a priceless prototype chip was swapped with a blank shell during the launch demo",
        "hook": "The demo still worked for a few seconds because someone had prepared a fake signal.",
        "locations": ["Demo Stage", "Server Closet", "Rooftop Lounge"],
    },
    {
        "name": "luxury train carriage",
        "case_type": "diamond theft",
        "object": "black diamond cufflink pair",
        "victim_role": "private collector",
        "incident": "a pair of black diamond cufflinks vanished from a locked luggage case between two stations",
        "hook": "The case key never left the collector's chain, but the velvet lining was warm.",
        "locations": ["Dining Car", "Luggage Bay", "Observation Car"],
    },
    {
        "name": "botanical conservatory",
        "case_type": "poisoning",
        "object": "toxic orchid extract",
        "victim_role": "plant geneticist",
        "incident": "a plant geneticist was poisoned with extract from a rare orchid kept under glass",
        "hook": "The orchid case looked untouched, yet the misting system ran outside its schedule.",
        "locations": ["Palm House", "Mist Room", "Visitor Gallery"],
    },
    {
        "name": "private film studio",
        "case_type": "sabotage and theft",
        "object": "ruby-studded prop crown",
        "victim_role": "studio producer",
        "incident": "a ruby-studded crown vanished after a stunt rig failed on set",
        "hook": "The accident drew everyone away, but the crown had already been replaced with a lighter copy.",
        "locations": ["Editing Suite", "Prop Store", "Screening Room"],
    },
    {
        "name": "sealed auction house",
        "case_type": "art theft",
        "object": "miniature royal portrait with hidden emeralds",
        "victim_role": "auction appraiser",
        "incident": "a miniature royal portrait with hidden emeralds disappeared before sealed bidding began",
        "hook": "The thief left the frame behind, as if they knew the emeralds mattered more than the painting.",
        "locations": ["Viewing Room", "Vault Hall", "Phone Bidding Desk"],
    },
    {
        "name": "coastal research lab",
        "case_type": "research sabotage",
        "object": "rare pearl sample",
        "victim_role": "marine researcher",
        "incident": "a rare pearl sample was stolen and a freezer alarm was triggered to distract the lab staff",
        "hook": "The alarm looked accidental until the backup temperature log showed a neat four-minute gap.",
        "locations": ["Sample Freezer", "Dock Tunnel", "Lab Office"],
    },
    {
        "name": "royal wedding rehearsal",
        "case_type": "necklace theft",
        "object": "queen's emerald choker",
        "victim_role": "wedding planner",
        "incident": "the queen's emerald choker vanished during a crowded rehearsal",
        "hook": "The empty case was placed back under the veil table before the bride entered.",
        "locations": ["Dressing Suite", "Flower Hall", "Chapel Aisle"],
    },
    {
        "name": "casino charity night",
        "case_type": "murder and chip theft",
        "object": "platinum charity chips",
        "victim_role": "casino host",
        "incident": "the casino host was found dead as a tray of platinum charity chips disappeared",
        "hook": "The chips were heavy enough to slow the thief, but the nearest exit stayed closed.",
        "locations": ["Roulette Floor", "Cashier Cage", "Private Balcony"],
    },
]

CRIME_SCENE_TYPES = [
    "murder",
    "attempted murder",
    "poisoning",
    "sabotage",
    "blackmail",
    "arson",
    "kidnapping",
    "assault",
    "disappearance",
    "jewel theft",
    "art theft",
    "artifact theft",
    "prototype theft",
]

FALLBACK_NAMES = [
    ("Avery Rao", "restoration specialist"),
    ("Nila Ward", "donor liaison"),
    ("Omar Finch", "security engineer"),
    ("Leah Suri", "research assistant"),
    ("Dev Malik", "systems technician"),
    ("Iris Cole", "event coordinator"),
]

_last_theme_name: str | None = None
_last_crime_type: str | None = None

FORBIDDEN_PUBLIC_HINTS = [
    "acting strangely",
    "bloody",
    "clear my name",
    "confession",
    "culprit",
    "empty vial",
    "evidence",
    "fingerprint",
    "fresh footprints",
    "guilty",
    "hidden path",
    "important",
    "innocent",
    "key clue",
    "never harm",
    "nervous",
    "planted",
    "points to",
    "prove",
    "recently used",
    "reveals",
    "secret note",
    "solid alibi",
    "strong substance",
    "suspicious",
    "suspiciously",
    "tampered",
    "this proves",
    "unusual",
    "worried",
]

ASCII_TEXT_FIELDS = [
    "title",
    "crime_story",
    "victim",
    "case_type",
    "timeline_summary",
    "red_herrings",
    "verdict_reason",
]

SOFT_PUBLIC_REPLACEMENTS = {
    "acting strangely": "moving quickly",
    "anything suspicious": "anything after that",
    "anything unusual": "anything after that",
    "clear my name": "settle the facts",
    "i would never harm": "I had no quarrel with",
    "never harm": "had no quarrel with",
    "nervous": "rushed",
    "prove": "show",
    "shocked": "trying to understand what happened",
    "solid alibi": "account",
    "suspicious": "out of place",
    "unusual": "out of place",
    "worried": "quiet",
}


def _choose_theme(recent_case_summaries: list[str] | None = None) -> dict:
    global _last_theme_name
    recent_text = " ".join(recent_case_summaries or []).lower()
    recent_theft_heavy = any(word in recent_text for word in ["theft", "stolen", "vanished", "disappeared"])
    choices = [
        theme
        for theme in CASE_THEMES
        if theme["name"] != _last_theme_name
        and theme["name"].lower() not in recent_text
        and not (recent_theft_heavy and "theft" in theme["case_type"])
    ]
    if not choices:
        choices = [theme for theme in CASE_THEMES if theme["name"] != _last_theme_name] or CASE_THEMES
    theme = random.choice(choices)
    _last_theme_name = theme["name"]
    return theme


def _choose_crime_type(recent_case_summaries: list[str] | None = None) -> str:
    global _last_crime_type
    recent_text = " ".join(recent_case_summaries or []).lower()
    choices = [
        crime_type
        for crime_type in CRIME_SCENE_TYPES
        if crime_type != _last_crime_type and crime_type.lower() not in recent_text
    ]
    if not choices:
        choices = [crime_type for crime_type in CRIME_SCENE_TYPES if crime_type != _last_crime_type] or CRIME_SCENE_TYPES
    crime_type = random.choice(choices)
    _last_crime_type = crime_type
    return crime_type


class CaseWorkflowState(TypedDict, total=False):
    request: CaseCreateRequest
    recent_case_summaries: list[str]
    case: MysteryCase
    ai_provider: str
    validation_notes: str
    error: str


class ExplanationState(TypedDict, total=False):
    case: MysteryCase
    selected_suspect_id: str
    player_name: str
    result: AccusationResult


def _llm(settings: Settings) -> ChatGroq | None:
    if not settings.groq_api_key or settings.groq_api_key.lower() in {"fallback", "disabled", "none"}:
        return None
    return ChatGroq(api_key=settings.groq_api_key, model=settings.groq_model, temperature=0.7)


def _json_from_text(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response.")
    return json.loads(cleaned[start : end + 1])


def _subtlety_problems(case: MysteryCase) -> list[str]:
    public_text_parts: list[str] = [
        case.crime_story,
        *case.timeline_summary,
    ]
    for scene in case.scenes:
        public_text_parts.extend([scene.title, scene.character_name, scene.description, scene.atmosphere])
        for clue in scene.clues:
            public_text_parts.extend([clue.title, clue.detail])
    for suspect in case.suspects:
        public_text_parts.append(suspect.statement)

    public_text = "\n".join(public_text_parts).lower()
    return [term for term in FORBIDDEN_PUBLIC_HINTS if term in public_text]


def _english_text_problems(case: MysteryCase) -> list[str]:
    text_parts: list[str] = []
    for field in ASCII_TEXT_FIELDS:
        value = getattr(case, field)
        if isinstance(value, list):
            text_parts.extend(str(item) for item in value)
        else:
            text_parts.append(str(value))
    for scene in case.scenes:
        text_parts.extend([scene.title, scene.character_name, scene.description, scene.atmosphere])
        for clue in scene.clues:
            text_parts.extend([clue.title, clue.detail])
    for suspect in case.suspects:
        text_parts.extend([suspect.name, suspect.role, suspect.statement, suspect.motive, suspect.alibi, suspect.suspicious_detail])
        text_parts.extend(suspect.timeline)
    for link in case.evidence_chain:
        text_parts.extend([link.clue_id, link.reasoning])

    combined = "\n".join(text_parts)
    if combined.isascii():
        return []
    return sorted({char for char in combined if not char.isascii()})[:8]


def _soften_public_hint_language(case: MysteryCase) -> MysteryCase:
    def soften(text: str) -> str:
        updated = text
        for source, replacement in SOFT_PUBLIC_REPLACEMENTS.items():
            updated = updated.replace(source, replacement)
            updated = updated.replace(source.capitalize(), replacement.capitalize())
        return updated

    case.crime_story = soften(case.crime_story)
    case.timeline_summary = [soften(event) for event in case.timeline_summary]
    for scene in case.scenes:
        scene.title = soften(scene.title)
        scene.description = soften(scene.description)
        scene.atmosphere = soften(scene.atmosphere)
        for clue in scene.clues:
            clue.title = soften(clue.title)
            clue.detail = soften(clue.detail)
    for suspect in case.suspects:
        suspect.statement = soften(suspect.statement)
    return case


def _fallback_case(request: CaseCreateRequest, recent_case_summaries: list[str] | None = None) -> MysteryCase:
    theme = _choose_theme(recent_case_summaries)
    suspects_seed = random.sample(FALLBACK_NAMES, 3)
    culprit_name, culprit_role = suspects_seed[0]
    suspect_two_name, suspect_two_role = suspects_seed[1]
    suspect_three_name, suspect_three_role = suspects_seed[2]
    victim_first = random.choice(["Mira", "Rohan", "Elena", "Kabir", "Tara", "Noah"])
    victim = f"{victim_first} Sen, {theme['victim_role']}"
    object_name = theme["object"]
    case_type = theme["case_type"]
    incident = theme["incident"]
    hook = theme["hook"]
    loc_one, loc_two, loc_three = theme["locations"]
    case = MysteryCase(
        title=f"The {theme['name'].title()} Mystery",
        difficulty=request.difficulty,
        case_type=case_type,
        victim=victim,
        crime_story=(
            f"During a private event at the {theme['name']}, {incident}. "
            "Three people were nearby, and each had a reason to hide where they really were. "
            f"{hook} The case turns on a quiet contradiction between what people said and what the rooms show."
        ),
        scenes=[],
        suspects=[],
        accused_id="suspect_1",
        timeline_summary=[
            f"Guests gather near the {loc_three.lower()} while the {object_name} is still secured.",
            f"{suspect_two_name} has a tense exchange with {victim_first}.",
            f"A short disruption draws attention toward the {loc_one.lower()}.",
            f"A staff-only path near the {loc_two.lower()} becomes part of the investigation.",
            f"The {case_type} is discovered after the room is checked again.",
        ],
        evidence_chain=[
            {"clue_id": "clue_access", "reasoning": f"The staff-only entry uses access associated with {culprit_name}'s role."},
            {"clue_id": "clue_transfer", "reasoning": f"The small transfer mark links {culprit_name} to the handled storage case."},
            {"clue_id": "clue_signal", "reasoning": f"{culprit_name}'s statement avoids the restricted path, but the access and room details place them there."},
        ],
        red_herrings=[
            f"{suspect_two_name} has the loudest motive, but the mark linked to them comes from earlier event material.",
            f"{suspect_three_name} has system access, but their explanation fits the service problem better than the physical trace.",
        ],
        verdict_reason=(
            f"{culprit_name} is the liar. Their statement says they stayed away from the restricted path, but the access record, "
            f"transfer mark, and signal record place them near the {object_name}. {suspect_two_name} and {suspect_three_name} raise doubts, "
            "but their statements still fit the room details."
        ),
        validated=True,
        validation_notes="Fallback case is internally consistent.",
    )
    scene_one_id = "scene_one"
    scene_two_id = "scene_two"
    scene_three_id = "scene_three"
    case.scenes = [
        {
            "id": scene_one_id,
            "title": loc_one,
            "character_name": culprit_name,
            "description": (
                f"{culprit_name} was seen near the {loc_one.lower()} before the lights failed. "
                f"The room was calm after power returned, but the storage case had been moved slightly from its usual line. "
                "Nothing looked broken, which made the scene feel ordinary at first. "
                "The odd part was how neatly everything had been put back."
            ),
            "atmosphere": "Quiet, tense, and carefully arranged.",
            "clues": [
                {
                    "id": "clue_transfer",
                    "title": "Small Transfer Mark",
                    "detail": f"A faint mark on {culprit_name}'s sleeve matches the storage case edge.",
                    "scene_id": scene_one_id,
                    "points_to": ["suspect_1"],
                    "reliability": "high",
                },
                {
                    "id": "clue_old_note",
                    "title": "Old Note",
                    "detail": f"A note near the scene carries {suspect_two_name}'s handwriting, but it appears to be from earlier setup work.",
                    "scene_id": scene_one_id,
                    "points_to": ["suspect_2"],
                    "reliability": "medium",
                }
            ],
        },
        {
            "id": scene_two_id,
            "title": loc_two,
            "character_name": suspect_three_name,
            "description": (
                f"{suspect_three_name} was working near the {loc_two.lower()} when the power problem began. "
                "A staff door opened during the blackout, and the sound blended into the noise of people moving around. "
                "The log was incomplete, so it did not name a person directly. "
                "The missing name made the entry feel unfinished."
            ),
            "atmosphere": "Narrow, noisy, and hard to watch clearly.",
            "clues": [
                {
                    "id": "clue_access",
                    "title": "Access Record",
                    "detail": f"The staff-only entry uses an access group available to {culprit_name}, while {suspect_three_name} could manage the system.",
                    "scene_id": scene_two_id,
                    "points_to": ["suspect_1", "suspect_3"],
                    "reliability": "high",
                },
                {
                    "id": "clue_signal",
                    "title": "Signal Record",
                    "detail": f"{culprit_name}'s device stayed near the staff path during the blackout.",
                    "scene_id": scene_two_id,
                    "points_to": ["suspect_1"],
                    "reliability": "medium",
                },
            ],
        },
        {
            "id": scene_three_id,
            "title": loc_three,
            "character_name": suspect_two_name,
            "description": (
                f"{suspect_two_name} returned to the {loc_three.lower()} soon after a tense conversation with {victim_first}. "
                "Several people remembered the argument, but not the exact minute it ended. "
                "A dropped event item made the area look more important than it really was. "
                "The crowd made every short absence difficult to judge."
            ),
            "atmosphere": "Crowded, warm, and full of half-remembered movement.",
            "clues": [
                {
                    "id": "clue_argument",
                    "title": "Public Argument",
                    "detail": f"{suspect_two_name} argued with {victim_first} and had a brief gap before being seen again.",
                    "scene_id": scene_three_id,
                    "points_to": ["suspect_2"],
                    "reliability": "medium",
                },
                {
                    "id": "clue_reset",
                    "title": "Work Log",
                    "detail": f"{suspect_three_name}'s work log mentions the same staff door but leaves the entry unnamed.",
                    "scene_id": scene_three_id,
                    "points_to": ["suspect_3"],
                    "reliability": "high",
                },
            ],
        },
    ]
    case.suspects = [
        {
            "id": "suspect_1",
            "name": culprit_name,
            "role": culprit_role.title(),
            "statement": f"I never went near the {loc_two.lower()} during the disruption. I stayed away from the staff-only path and only returned after people started asking questions.",
            "motive": f"{culprit_name} needed the {object_name} to solve a private problem and had enough inside knowledge to know when it would be least guarded. The motive is not loud, but it is practical.",
            "alibi": f"{culprit_name} says they were away from the restricted path during the disruption. The statement sounds simple, but the room records do not fully support it.",
            "timeline": [f"seen near the {loc_one.lower()}", f"connected to the staff path near {loc_two.lower()}", f"returns toward the {loc_three.lower()}"],
            "suspicious_detail": f"A small transfer mark and a device signal place {culprit_name} closer to the missing {object_name} than the alibi allows.",
        },
        {
            "id": "suspect_2",
            "name": suspect_two_name,
            "role": suspect_two_role.title(),
            "statement": f"I argued with {victim_first}, yes, but I came back through the {loc_three.lower()}. Plenty of people saw me trying to calm things down.",
            "motive": f"{suspect_two_name} was under pressure after a public disagreement with {victim_first}. Taking the {object_name} would have given them leverage.",
            "alibi": f"{suspect_two_name} was seen around the guests again after the argument. A personal item near the scene makes the account look worse.",
            "timeline": [f"leaves the {loc_three.lower()} after an argument", "seen near guests again", "reports concern to staff"],
            "suspicious_detail": f"{suspect_two_name} has a strong motive and a visible argument, but the physical trace comes from earlier event material.",
        },
        {
            "id": "suspect_3",
            "name": suspect_three_name,
            "role": suspect_three_role.title(),
            "statement": f"I was handling the system issue near the {loc_two.lower()}. The access logs look strange because I was trying to restore power, not because I took anything.",
            "motive": f"{suspect_three_name} could benefit if blame fell on a system failure instead of a person. Their work gave them access to logs and locked paths.",
            "alibi": f"{suspect_three_name} says they were handling a technical issue during the disruption. The log supports part of it, but also connects them to the access system.",
            "timeline": [f"near the {loc_two.lower()}", "starts system work", "responds after the alarm"],
            "suspicious_detail": f"{suspect_three_name} can explain the system activity, but the same explanation makes them look involved.",
        },
    ]
    return MysteryCase.model_validate(
        {
            **case.model_dump(exclude={"scenes", "suspects"}),
            "scenes": case.scenes,
            "suspects": case.suspects,
        }
    )


def build_case_workflow(settings: Settings):
    llm = _llm(settings)

    def case_generator(state: CaseWorkflowState) -> CaseWorkflowState:
        request = state["request"]
        required_crime_type = _choose_crime_type(state.get("recent_case_summaries", []))
        if llm is None:
            return {
                **state,
                "case": _fallback_case(request, state.get("recent_case_summaries", [])),
                "ai_provider": "fallback",
            }

        prompt = {
            "creative_seed": uuid4().hex,
            "difficulty": request.difficulty,
            "avoid_similar_to": state.get("recent_case_summaries", []),
            "required_crime_type": required_crime_type,
            "generate_freely": {
                "instruction": "Invent a completely new high-stakes mystery. Do not choose from a predefined list.",
                "allowed_crime_types": [
                    "murder",
                    "attempted murder",
                    "poisoning",
                    "sabotage",
                    "blackmail connected to a serious crime",
                    "arson",
                    "kidnapping",
                    "assault",
                    "disappearance",
                    "jewel theft",
                    "art theft",
                    "artifact theft",
                    "prototype theft",
                ],
                "avoid_low_stakes_focus": [
                    "missing book",
                    "missing diary",
                    "missing map",
                    "ordinary document",
                    "generic data file",
                    "simple office theft",
                ],
            },
        }
        messages = [
            SystemMessage(
                content=(
                    "You are a Case Generator Agent for an AI mystery game. Return only valid JSON matching this schema: "
                    "title, difficulty, crime_story, victim, case_type, scenes, suspects, accused_id, timeline_summary, "
                    "evidence_chain, red_herrings, verdict_reason. Use exactly 3 suspects and exactly 3 scenes. "
                    "Use string ids only: suspects must be suspect_1, suspect_2, suspect_3; scenes must be scene_1, scene_2, scene_3; clues must use string ids like clue_1. "
                    "Each scene object must include id, title, character_name, description, atmosphere, and clues. "
                    "Each clues value must be an array of 1-2 clue objects, never a string. Each clue object must include id, title, detail, scene_id, points_to, and reliability. "
                    "points_to must be an array of suspect id strings, and reliability must be low, medium, or high. "
                    "Each suspect must include id, name, role, statement, motive, alibi, timeline, and suspicious_detail. "
                    "Each suspect timeline must be an array of short neutral background notes, never one combined string. Do not use clock times or chronological deduction as the solution mechanic. "
                    "timeline_summary must be an array of 3-5 broad case context notes for backend compatibility only, not a player-facing solution path. evidence_chain must be an array of objects with clue_id and reasoning. "
                    "red_herrings must be an array of strings. Do not use prose strings where the schema requires arrays or objects. "
                    "All generated text must be in English only. Use ASCII English letters, numbers, and standard punctuation only. "
                    "Do not use Chinese, Hindi, Japanese, Korean, Arabic, accented Latin characters, or any non-English words or symbols in names, places, clues, dialogue, or explanations. "
                    f"The required case_type for this case is {required_crime_type}. Use this crime type directly and build the mystery around it. "
                    "Do not turn murder, poisoning, sabotage, arson, kidnapping, assault, disappearance, or blackmail into a hidden theft plot. "
                    "Only make theft the central crime when the required case_type explicitly contains theft. "
                    "The player sees only the scene descriptions and suspect statements. The game is about detecting which suspect is lying. "
                    "Exactly one suspect statement must be false, and accused_id must be the id of that lying suspect. "
                    "The other two suspect statements must be mostly true but still sound suspicious enough to create doubt. "
                    "Write each suspect statement in first person, 2-3 simple sentences, as if they are defending themselves in interrogation. "
                    "Do not make the liar obvious by sounding too nervous, confessing, or contradicting themselves directly inside the statement. "
                    "Suspect statements must sound natural and specific. Avoid generic warning words like suspicious, unusual, shocked, worried, guilty, innocent, clue, evidence, or prove. "
                    "Each scene must focus on a different suspect or important character by name. "
                    "Invent the case theme yourself. Do not select from a fixed list, and do not repeat common examples like museum gala, observatory, hotel kitchen, train carriage, auction house, or research lab unless you transform them into a fresh setting. "
                    "Invent all character names, roles, crime method, harm or stakes, locations, motive web, relationships, scene details, and twist dynamically. "
                    "Scene descriptions are shown to players, so write them as neutral event descriptions only: "
                    "3-4 short lines, simple words, and no direct hints. Never use warning or solution-signpost phrases like "
                    "'this proves', 'points to', 'reveals', 'suggests', 'important', 'key clue', 'suspiciously', 'culprit', 'guilty', or 'innocent'. "
                    "Every clue must feel like an ordinary part of the story world: a misplaced cup, a changed routine, a damp sleeve, a changed label, "
                    "a half-heard sentence, a receipt, a smell, a smudge, a polite interruption, or an object detail that characters would naturally notice. "
                    "Never make a clue an obvious crime object or direct forensic sign: no empty poison vial, bloody weapon, fingerprint match, torn confession, secret note naming the culprit, "
                    "fresh footprints, recently used hidden path, or phrase that says something was clearly tampered with. "
                    "Do not describe clues with evaluative wording like recently used, strong substance, suspicious, unusual, important, deliberate, planted, or hidden. "
                    "If the case involves poison, murder, theft, or sabotage, the public clues should be normal nearby details such as a menu change, a tray arrangement, a rewritten label, "
                    "a moved chair, a dry glass ring, a missing glove from a pair, a corrected receipt, or a harmless-looking access note. "
                    "The twist must be woven into normal scene texture. It should become meaningful after comparing scene facts, suspect statements, relationships, object placement, behavior, access, or motive pressure. "
                    "Do not use timing as the solution. Do not explain the twist inside a scene, clue detail, motive, alibi, or suspicious_detail. "
                    "Clue details may exist in JSON for internal reasoning, but each detail must be subtle, ambiguous, and plausible for more than one suspect at first glance. "
                    "No single clue may name or directly identify the accused. Each suspect should have one detail that could make them look involved, "
                    "while only the combined evidence_chain resolves the lie. "
                    "Write suspicious_detail as a neutral oddity, not as an accusation or conclusion. "
                    "Prefer varied high-stakes mysteries: murder, attempted murder, poison, sabotage, blackmail, arson, kidnapping, assault, disappearance, jewel theft, art theft, artifact theft, or prototype theft. "
                    "Avoid making the main mystery only a missing book, diary, map, ordinary document, or generic data file. If a document appears, connect it to murder, blackmail, jewels, poison, or another serious crime. "
                    "Make the plot feel dramatic but still believable, with a clear victim, danger, public scandal, damaged relationship, or serious loss. "
                    "Use globally varied fictional names from many cultures, as if inspired by broad real-world naming patterns, but do not use famous real people or public figures. "
                    "Do not reuse Avery, Nila, Omar, Mira, archive, or service lift. "
                    "Each suspect must have a balanced 2-3 sentence motive, alibi, and suspicious_detail. "
                    "Do not make the guilty suspect obvious from a single clue, unusually dramatic behavior, or a uniquely weak alibi; give every suspect plausible motive and opportunity. "
                    "Red herrings should create doubt without fully clearing innocent suspects, and they should arise from natural story events rather than artificial distractions. "
                    "The liar must be provable by combining scene facts, suspect statements, motive pressure, access, object placement, behavior, and evidence_chain reasoning. "
                    "The evidence_chain may explain the hidden logic directly, but the public-facing scenes, statements, motives, alibis, and suspicious details must remain story-like and understated. "
                    "The verdict_reason must reveal how the ordinary details combine into the twist and explain which statement was false and why."
                )
            ),
            HumanMessage(content=json.dumps(prompt)),
        ]
        last_error: Exception | None = None
        for attempt in range(4):
            current_messages = list(messages)
            if last_error is not None:
                current_messages.append(
                    HumanMessage(
                        content=(
                            "The previous draft was rejected. Return a fresh case as valid JSON only. "
                            f"Fix this issue without adding warnings or direct clue language: {last_error}"
                        )
                    )
                )
            try:
                doc = _json_from_text(llm.invoke(current_messages).content)
                doc["difficulty"] = request.difficulty
                case = _soften_public_hint_language(MysteryCase.model_validate(doc))
                english_problems = _english_text_problems(case)
                if english_problems:
                    raise ValueError(
                        "Generated text must be English ASCII only. Non-English characters found: "
                        + " ".join(english_problems)
                    )
                subtlety_problems = _subtlety_problems(case)
                if subtlety_problems:
                    raise ValueError(
                        "Public-facing story text contains direct hint language: "
                        + ", ".join(subtlety_problems[:8])
                    )
                return {**state, "case": case, "ai_provider": "groq"}
            except Exception as exc:
                last_error = exc

        fallback = _fallback_case(request, state.get("recent_case_summaries", []))
        fallback.validation_notes = f"AI generation failed, fallback used: {last_error}"
        return {**state, "case": fallback, "ai_provider": "fallback", "error": str(last_error)}

    def logic_validator(state: CaseWorkflowState) -> CaseWorkflowState:
        case = state["case"]
        suspect_ids = {suspect.id for suspect in case.suspects}
        clue_ids = {clue.id for scene in case.scenes for clue in scene.clues}
        problems: list[str] = []
        if case.accused_id not in suspect_ids:
            problems.append("Accused id is not present in suspects.")
        for link in case.evidence_chain:
            if link.clue_id not in clue_ids:
                problems.append(f"Evidence link references missing clue {link.clue_id}.")
        if len(case.suspects) < 3:
            problems.append("Case should include at least three suspects.")
        if any(not suspect.statement.strip() for suspect in case.suspects):
            problems.append("Every suspect must include a non-empty interrogation statement.")
        if llm is not None and not problems:
            messages = [
                SystemMessage(
                    content=(
                        "You are a Logic Validator Agent. Check whether the accused is exactly the suspect whose interrogation statement is false. "
                        "Also check whether the other two statements can be true, whether scene descriptions avoid direct hints, "
                        "and whether the solution does not depend primarily on a public timeline. "
                        "Reply with concise validation notes only."
                    )
                ),
                HumanMessage(content=case.model_dump_json()),
            ]
            try:
                notes = llm.invoke(messages).content.strip()
            except Exception as exc:
                notes = f"Structural validation passed. LLM validation unavailable: {exc}"
        else:
            notes = " ".join(problems) if problems else "Structural validation passed."

        case.validated = not problems
        case.validation_notes = notes
        return {**state, "case": case, "validation_notes": notes}

    graph = StateGraph(CaseWorkflowState)
    graph.add_node("case_generator", case_generator)
    graph.add_node("logic_validator", logic_validator)
    graph.set_entry_point("case_generator")
    graph.add_edge("case_generator", "logic_validator")
    graph.add_edge("logic_validator", END)
    return graph.compile()


def build_explanation_workflow(settings: Settings):
    llm = _llm(settings)

    def explanation_agent(state: ExplanationState) -> ExplanationState:
        case = state["case"]
        selected_id = state["selected_suspect_id"]
        selected = next((suspect for suspect in case.suspects if suspect.id == selected_id), None)
        correct = next((suspect for suspect in case.suspects if suspect.id == case.accused_id), None)
        is_correct = selected_id == case.accused_id

        if llm is None:
            explanation = (
                f"{'Correct' if is_correct else 'Incorrect'}. The evidence proves {correct.name if correct else 'the true culprit'} "
                f"committed the crime. {case.verdict_reason}"
            )
        else:
            messages = [
                SystemMessage(
                    content=(
                        "You are an Explanation Agent. Explain the verdict in a satisfying detective style. "
                        "Use the evidence chain, scene details, suspect statements, motive pressure, behavior, and access. "
                        "The player is trying to identify who lied in interrogation. "
                        "If the player was wrong, explain why their selected suspect's statement can still be true and identify the actual lie."
                    )
                ),
                HumanMessage(
                    content=json.dumps(
                        {
                            "player_name": state.get("player_name", "Detective"),
                            "selected_suspect": selected.model_dump() if selected else None,
                            "correct_suspect": correct.model_dump() if correct else None,
                            "is_correct": is_correct,
                            "case": case.model_dump(mode="json"),
                        }
                    )
                ),
            ]
            try:
                explanation = llm.invoke(messages).content.strip()
            except Exception:
                explanation = (
                    f"{'Correct' if is_correct else 'Incorrect'}. {case.verdict_reason}"
                )

        result = AccusationResult(
            case_id=case.id,
            selected_suspect_id=selected_id,
            correct_suspect_id=case.accused_id,
            is_correct=is_correct,
            explanation=explanation,
            evidence_chain=case.evidence_chain,
        )
        return {**state, "result": result}

    graph = StateGraph(ExplanationState)
    graph.add_node("explanation_agent", explanation_agent)
    graph.set_entry_point("explanation_agent")
    graph.add_edge("explanation_agent", END)
    return graph.compile()
