from app.utils.text import normalize_text


def test_normalize_text():
    assert normalize_text("Développeur Python/SAP!!") == "developpeur python/sap"
