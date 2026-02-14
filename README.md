# CV Matcher (FastAPI + React + MongoDB + ChromaDB)

Application full-stack pour matcher une base persistante de CV contre des appels d'offres (AO), avec scoring déterministe orienté keywords + preuves.

## Architecture
- `backend/`: API FastAPI, parsing CV/AO (PDF/DOCX/TXT), index lexical, embeddings, scoring déterministe.
- `frontend/`: UI React/Vite (TypeScript) avec pages CV Library, AO, Matching.
- `mongo`: persistance des documents métier.
- `chroma`: persistance des embeddings des chunks CV (`cv_chunks`).

## Arborescence
```text
backend/
  app/
  resources/keyword_rules.yml
  tests/
frontend/
docker-compose.yml
README.md
```

## Démarrage (Docker Compose - dev)
```bash
docker compose up --build
```

URLs:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Variables d'environnement
Copier `.env.example` vers `.env` puis adapter au besoin.

## Workflow produit
1. **Importer des CV** (une seule fois):
   - UI: `CV Library` > sélectionner plusieurs fichiers > `Importer CV`.
   - API: `POST /api/cvs/upload` multipart `files`.
2. **Créer un AO**:
   - UI: `Appels d’offres` > upload fichier ou coller texte > `Ajouter AO`.
   - API: `POST /api/rfps` avec `file` ou `text`.
3. **Lancer matching**:
   - UI: `Matching` > sélectionner AO > `Matcher`.
   - API: `POST /api/match/run` avec `{ "rfp_id": "...", "top_n": 10, "debug": true }`.
4. **Consulter run**:
   - API: `GET /api/match/run/{run_id}`.

## Score (déterministe)
- must (70%), important (20%), coherence embedding (10%).
- pénalités configurable env (`PENALTY_MISSING_MUST`, `PENALTY_TOO_SEMANTIC`).
- types de match tracés: exact, alias, deduction, semantic, none.
- preuves obligatoires: extrait chunk + source_ref.

## Tests
Depuis le dossier `backend/`:
```bash
pytest -q
```

Couverts:
- `normalize_text()`
- `expand_keywords_from_rules()`
- `keyword_extraction_basic()`
- `scoring_deterministic()`

## Checkpoints git recommandés
1. `chore: bootstrap backend fastapi + mongo + chroma`
2. `feat: cv ingestion parsing chunking embedding`
3. `feat: rfp extraction + keyword rules + deterministic scoring`
4. `feat: matching API + persistent runs/results`
5. `feat: frontend pages cv/rfp/matching`
6. `test: add unit tests and docs`

## Notes sécurité
- Pas de logging du texte CV complet.
- Secrets via `.env`.
- CORS configuré côté backend.
