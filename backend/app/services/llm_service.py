from app.core.config import settings


class LLMService:
    async def structure_rfp(self, text: str, heuristic: dict[str, list[str]]) -> dict:
        # Deterministic mock-first structure to keep auditability.
        role_title = "Unknown Role"
        for line in text.splitlines()[:20]:
            if line.strip():
                role_title = line.strip()[:80]
                break
        return {
            "role_title": role_title,
            "missions": text[:1000],
            "must_have": heuristic.get("must_have", []),
            "important": heuristic.get("important", []),
            "context": heuristic.get("context", []),
            "language": "fr" if " le " in text.lower() else "en",
            "notes": f"provider={settings.llm_provider}",
            "ambiguities": [],
        }
