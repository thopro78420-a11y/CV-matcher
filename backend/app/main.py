from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.chroma import init_chroma
from app.db.mongo import close_mongo, connect_mongo

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_mongo()
    init_chroma()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)
