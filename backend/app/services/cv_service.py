from datetime import datetime
from uuid import uuid4

from bson import ObjectId

from app.db.chroma import get_collection
from app.db.mongo import get_database
from app.services.embedding_service import EmbeddingService
from app.services.parser_service import ParserService
from app.utils.text import chunk_text, detect_language


class CVService:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.parser = ParserService()

    async def upload(self, files):
        db = get_database()
        collection = get_collection()
        results = []
        for file in files:
            content = await file.read()
            text = self.parser.extract_text(file.filename, content)
            language = detect_language(text)
            candidate_id = str(uuid4())
            doc = {
                "candidate_id": candidate_id,
                "name": file.filename,
                "language": language,
                "created_at": datetime.utcnow(),
                "status": "indexed",
            }
            await db.candidates.insert_one(doc)
            chunks = chunk_text(text)
            chunk_docs = []
            ids = []
            embeddings = []
            docs_text = []
            metas = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{candidate_id}_{i}"
                section = "skills" if i == 0 else "experience"
                chunk_docs.append(
                    {
                        "candidate_id": candidate_id,
                        "chunk_id": chunk_id,
                        "text": chunk,
                        "section": section,
                        "source_file": file.filename,
                    }
                )
                ids.append(chunk_id)
                emb = self.embedder.embed(chunk)
                embeddings.append(emb)
                docs_text.append(chunk)
                metas.append({"candidate_id": candidate_id, "chunk_id": chunk_id, "section": section, "source_file": file.filename})
            if chunk_docs:
                await db.cv_chunks.insert_many(chunk_docs)
                collection.add(ids=ids, embeddings=embeddings, documents=docs_text, metadatas=metas)
            await db.cv_documents.insert_one(
                {
                    "candidate_id": candidate_id,
                    "filename": file.filename,
                    "raw_text": text,
                    "uploaded_at": datetime.utcnow(),
                }
            )
            results.append({"candidate_id": candidate_id, "filename": file.filename, "chunks": len(chunks)})
        return results

    async def list_cvs(self):
        db = get_database()
        docs = []
        async for c in db.candidates.find().sort("created_at", -1):
            c["id"] = str(c.pop("_id"))
            docs.append(c)
        return docs

    async def get_cv(self, candidate_id: str):
        db = get_database()
        candidate = await db.candidates.find_one({"candidate_id": candidate_id})
        if not candidate:
            return None
        doc = await db.cv_documents.find_one({"candidate_id": candidate_id})
        chunks = []
        async for ch in db.cv_chunks.find({"candidate_id": candidate_id}):
            ch["id"] = str(ch.pop("_id"))
            chunks.append(ch)
        candidate["id"] = str(candidate.pop("_id"))
        candidate["document"] = {"filename": doc.get("filename"), "raw_text": doc.get("raw_text", "")[:5000]} if doc else None
        candidate["chunks"] = chunks
        return candidate

    async def delete_cv(self, candidate_id: str):
        db = get_database()
        await db.candidates.delete_many({"candidate_id": candidate_id})
        await db.cv_documents.delete_many({"candidate_id": candidate_id})
        await db.cv_chunks.delete_many({"candidate_id": candidate_id})
        collection = get_collection()
        records = collection.get(where={"candidate_id": candidate_id})
        ids = records.get("ids", []) if records else []
        if ids:
            collection.delete(ids=ids)
        return {"deleted": candidate_id}
