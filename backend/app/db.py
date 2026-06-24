from motor.motor_asyncio import AsyncIOMotorClient

from app.settings import Settings


class MongoStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: AsyncIOMotorClient | None = None

    async def connect(self) -> None:
        if not self.settings.mongodb_uri or self.settings.mongodb_uri.lower() in {"memory", "disabled", "none"}:
            return
        self.client = AsyncIOMotorClient(self.settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        await self.client.admin.command("ping")

    async def close(self) -> None:
        if self.client:
            self.client.close()

    @property
    def db(self):
        if not self.client:
            return None
        return self.client[self.settings.database_name]

    async def save_case(self, case_doc: dict) -> None:
        if self.db is None:
            return
        await self.db.cases.replace_one({"id": case_doc["id"]}, case_doc, upsert=True)

    async def get_case(self, case_id: str) -> dict | None:
        if self.db is None:
            return None
        doc = await self.db.cases.find_one({"id": case_id}, {"_id": 0})
        return doc

    async def save_history(self, history_doc: dict) -> None:
        if self.db is None:
            return
        await self.db.player_history.insert_one(history_doc)

    async def recent_cases(self, limit: int = 8) -> list[dict]:
        if self.db is None:
            return []
        cursor = self.db.cases.find({}, {"_id": 0, "title": 1, "crime_story": 1}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
