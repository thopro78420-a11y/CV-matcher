from pathlib import Path

import yaml

from app.utils.text import normalize_text


class KeywordService:
    def __init__(self) -> None:
        rules_path = Path(__file__).resolve().parents[2] / "resources" / "keyword_rules.yml"
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f) or {}

    def expand_keywords_from_rules(self, keywords: list[str]) -> dict[str, list[str]]:
        aliases = self.rules.get("aliases", {})
        result: dict[str, list[str]] = {}
        for keyword in keywords:
            canonical = normalize_text(keyword)
            expanded = {canonical}
            for base, variants in aliases.items():
                if canonical == normalize_text(base) or canonical in [normalize_text(v) for v in variants]:
                    expanded.add(normalize_text(base))
                    expanded.update(normalize_text(v) for v in variants)
            result[keyword] = sorted(v for v in expanded if v)
        return result

    def extract_keywords_basic(self, text: str) -> dict[str, list[str]]:
        normalized = normalize_text(text)
        tokens = set(normalized.split())
        aliases = self.rules.get("aliases", {})
        detected = []
        for base, variants in aliases.items():
            all_forms = [base, *variants]
            if any(normalize_text(form) in normalized for form in all_forms):
                detected.append(base)
            elif normalize_text(base).split()[0] in tokens:
                detected.append(base)
        must = detected[: min(5, len(detected))]
        important = detected[min(5, len(detected)) : min(10, len(detected))]
        context = list(tokens)[:10]
        return {
            "must_have": must,
            "important": important,
            "context": context,
        }
