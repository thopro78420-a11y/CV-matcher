from dataclasses import dataclass

from app.core.config import settings
from app.utils.text import normalize_text


@dataclass
class KeywordEvidence:
    keyword: str
    match_type: str
    chunk_text_excerpt: str
    source_ref: str


class ScoringService:
    match_type_weight = {
        "exact": 1.0,
        "alias": 0.9,
        "deduction": 0.8,
        "semantic": 0.7,
        "none": 0.0,
    }
    section_weight = {
        "skills": 1.0,
        "experience": 0.9,
        "other": 0.7,
    }

    def _score_keywords(self, keywords: list[str], chunks: list[dict], expanded: dict[str, list[str]]):
        found = []
        missing = []
        evidence: list[dict] = []
        deductions = []
        semantic_only = 0
        total = 0.0
        for kw in keywords:
            forms = expanded.get(kw, [normalize_text(kw)])
            best_score = 0.0
            best_match_type = "none"
            best_chunk = None
            for chunk in chunks:
                text_norm = normalize_text(chunk["text"])
                for idx, form in enumerate(forms):
                    if form and form in text_norm:
                        match_type = "exact" if idx == 0 else "alias"
                        if form != normalize_text(kw) and match_type == "alias":
                            deductions.append({"keyword": kw, "used_form": form, "rule": "alias_map"})
                        score = self.match_type_weight[match_type] * self.section_weight.get(chunk.get("section", "other"), 0.7)
                        if score > best_score:
                            best_score = score
                            best_match_type = match_type
                            best_chunk = chunk
            if best_score == 0 and chunks:
                # lightweight semantic fallback with proof from first chunk
                best_chunk = chunks[0]
                best_match_type = "semantic" if normalize_text(kw).split()[0] in normalize_text(chunks[0]["text"]) else "none"
                if best_match_type == "semantic":
                    best_score = self.match_type_weight["semantic"] * self.section_weight.get(best_chunk.get("section", "other"), 0.7)
                    semantic_only += 1
            total += best_score
            if best_score > 0:
                found.append(kw)
                evidence.append(
                    KeywordEvidence(
                        keyword=kw,
                        match_type=best_match_type,
                        chunk_text_excerpt=(best_chunk["text"][:240] if best_chunk else "Non trouvé dans le CV"),
                        source_ref=(best_chunk.get("chunk_id", "N/A") if best_chunk else "N/A"),
                    ).__dict__
                )
            else:
                missing.append(kw)
                evidence.append(
                    KeywordEvidence(
                        keyword=kw,
                        match_type="none",
                        chunk_text_excerpt="Non trouvé dans le CV",
                        source_ref="N/A",
                    ).__dict__
                )
        avg = (total / len(keywords)) * 100 if keywords else 100
        return avg, found, missing, evidence, deductions, semantic_only

    def scoring_deterministic(self, rfp: dict, candidate_chunks: list[dict], expanded: dict[str, list[str]], coherence: float):
        must = rfp.get("must_have", [])
        important = rfp.get("important", [])
        must_score, must_found, must_missing, must_evidence, deductions, sem_m = self._score_keywords(must, candidate_chunks, expanded)
        imp_score, imp_found, imp_missing, imp_evidence, deductions_i, sem_i = self._score_keywords(important, candidate_chunks, expanded)
        deductions.extend(deductions_i)
        raw = 0.7 * must_score + 0.2 * imp_score + 0.1 * (coherence * 100)
        penalties = 0
        penalties += len(must_missing) * settings.penalty_missing_must
        if sem_m + sem_i > max(1, len(must_found) + len(imp_found)):
            penalties += settings.penalty_too_semantic
        final = round(max(0, min(100, raw - penalties)), 2)
        return {
            "score_global": final,
            "must_found": {"count": len(must_found), "total": len(must), "found": must_found, "missing": must_missing},
            "important_found": {"count": len(imp_found), "total": len(important), "found": imp_found, "missing": imp_missing},
            "deductions_applied": deductions,
            "evidence": must_evidence + imp_evidence,
            "debug": {
                "must_score": must_score,
                "important_score": imp_score,
                "coherence": coherence,
                "raw": raw,
                "penalties": penalties,
            },
        }
