from datetime import datetime
from uuid import uuid4

from app.core.config import settings
from app.db.chroma import get_collection
from app.db.mongo import get_database
from app.services.embedding_service import EmbeddingService
from app.services.keyword_service import KeywordService
from app.services.scoring_service import ScoringService


class MatchService:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.keyword_service = KeywordService()
        self.scorer = ScoringService()

    async def run(self, rfp_id: str, top_n: int = 10, debug: bool = False):
        db = get_database()
        rfp = await db.rfps.find_one({"rfp_id": rfp_id})
        if not rfp:
            return None
        structured = rfp["structured"]
        query_text = " ".join([
            structured.get("role_title", ""),
            structured.get("missions", ""),
            " ".join(structured.get("must_have", [])),
            " ".join(structured.get("important", [])),
        ])
        query_emb = self.embedder.embed(query_text)
        chroma = get_collection()
        topk = chroma.query(query_embeddings=[query_emb], n_results=settings.max_topk_chunks)
        metadatas = topk.get("metadatas", [[]])[0] if topk else []
        candidate_ids = []
        for meta in metadatas:
            cid = meta.get("candidate_id")
            if cid and cid not in candidate_ids:
                candidate_ids.append(cid)
            if len(candidate_ids) >= settings.candidate_set_size:
                break
        if not candidate_ids:
            async for c in db.candidates.find().limit(settings.candidate_set_size):
                candidate_ids.append(c["candidate_id"])
        expanded = self.keyword_service.expand_keywords_from_rules(structured.get("must_have", []) + structured.get("important", []))
        results = []
        for cid in candidate_ids:
            chunks = []
            async for ch in db.cv_chunks.find({"candidate_id": cid}):
                chunks.append(ch)
            if not chunks:
                continue
            candidate_text = " ".join(ch["text"] for ch in chunks[:10])
            coherence = self.embedder.cosine_similarity(query_emb, self.embedder.embed(candidate_text))
            score = self.scorer.scoring_deterministic(structured, chunks, expanded, coherence)
            candidate = await db.candidates.find_one({"candidate_id": cid})
            results.append(
                {
                    "candidate_id": cid,
                    "candidate_name": candidate.get("name", cid) if candidate else cid,
                    **score,
                }
            )
        results.sort(key=lambda x: x["score_global"], reverse=True)
        run_id = str(uuid4())
        run_doc = {
            "run_id": run_id,
            "rfp_id": rfp_id,
            "debug": debug,
            "created_at": datetime.utcnow(),
            "result_ids": [],
        }
        inserted = []
        for rank, result in enumerate(results[:top_n], start=1):
            result_doc = {"run_id": run_id, "rank": rank, **result}
            insert_res = await db.match_results.insert_one(result_doc)
            inserted.append(str(insert_res.inserted_id))
        run_doc["result_ids"] = inserted
        await db.match_runs.insert_one(run_doc)
        return {"run_id": run_id, "results": results[:top_n]}

    async def get_run(self, run_id: str):
        db = get_database()
        run = await db.match_runs.find_one({"run_id": run_id})
        if not run:
            return None
        results = []
        async for r in db.match_results.find({"run_id": run_id}).sort("rank", 1):
            r["id"] = str(r.pop("_id"))
            results.append(r)
        run["id"] = str(run.pop("_id"))
        run["results"] = results
        return run
