from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CV Matcher"
    mongodb_uri: str = "mongodb://mongo:27017/cv_matcher"
    mongodb_db: str = "cv_matcher"
    chroma_persist_dir: str = "/data/chroma"
    llm_provider: str = "mock"
    llm_api_key: str = ""
    embeddings_provider: str = "local"
    embeddings_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embeddings_model: str = "text-embedding-3-small"
    cors_origins: str = "*"
    max_topk_chunks: int = 200
    candidate_set_size: int = 50
    penalty_missing_must: float = 15.0
    penalty_too_semantic: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
