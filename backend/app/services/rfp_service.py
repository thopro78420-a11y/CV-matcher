from datetime import datetime
from uuid import uuid4

from app.db.mongo import get_database
from app.services.keyword_service import KeywordService
from app.services.llm_service import LLMService
from app.services.parser_service import ParserService


class RFPService:
    def __init__(self):
        self.parser = ParserService()
        self.keyword_service = KeywordService()
        self.llm = LLMService()

    async def create_rfp(self, file=None, text: str | None = None):
        db = get_database()
        raw_text = text or ""
        filename = None
        if file is not None:
            content = await file.read()
            filename = file.filename
            raw_text = self.parser.extract_text(file.filename, content)
        heuristic = self.keyword_service.extract_keywords_basic(raw_text)
        structured = await self.llm.structure_rfp(raw_text, heuristic)
        rfp_id = str(uuid4())
        doc = {
            "rfp_id": rfp_id,
            "filename": filename,
            "raw_text": raw_text,
            "structured": structured,
            "created_at": datetime.utcnow(),
        }
        await db.rfps.insert_one(doc)
        return doc

    async def list_rfps(self):
        db = get_database()
        docs = []
        async for r in db.rfps.find().sort("created_at", -1):
            r["id"] = str(r.pop("_id"))
            docs.append(r)
        return docs

    async def get_rfp(self, rfp_id: str):
        db = get_database()
        r = await db.rfps.find_one({"rfp_id": rfp_id})
        if not r:
            return None
        r["id"] = str(r.pop("_id"))
        return r
