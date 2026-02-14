from app.services.scoring_service import ScoringService


def test_scoring_deterministic():
    scorer = ScoringService()
    rfp = {"must_have": ["python"], "important": ["sap s/4hana"]}
    chunks = [
        {"chunk_id": "c1", "text": "Expert Python et SAP S/4HANA", "section": "skills"},
    ]
    expanded = {"python": ["python"], "sap s/4hana": ["sap s/4hana", "s/4hana"]}
    first = scorer.scoring_deterministic(rfp, chunks, expanded, coherence=0.8)
    second = scorer.scoring_deterministic(rfp, chunks, expanded, coherence=0.8)
    assert first["score_global"] == second["score_global"]
    assert first["must_found"]["count"] == 1
