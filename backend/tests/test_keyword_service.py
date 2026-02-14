from app.services.keyword_service import KeywordService


def test_expand_keywords_from_rules():
    service = KeywordService()
    expanded = service.expand_keywords_from_rules(["S/4HANA"])
    assert "sap s/4hana" in expanded["S/4HANA"]
    assert "sap erp" in expanded["S/4HANA"]


def test_keyword_extraction_basic():
    service = KeywordService()
    data = service.extract_keywords_basic("Projet SAP S/4HANA et Python en gestion de projet")
    assert "sap s/4hana" in data["must_have"]
