from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.cv_service import CVService
from app.services.match_service import MatchService
from app.services.rfp_service import RFPService

router = APIRouter(prefix="/api")
cv_service = CVService()
rfp_service = RFPService()
match_service = MatchService()


@router.post("/cvs/upload")
async def upload_cvs(files: list[UploadFile] = File(...)):
    return await cv_service.upload(files)


@router.get("/cvs")
async def list_cvs():
    return await cv_service.list_cvs()


@router.get("/cvs/{candidate_id}")
async def get_cv(candidate_id: str):
    cv = await cv_service.get_cv(candidate_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


@router.delete("/cvs/{candidate_id}")
async def delete_cv(candidate_id: str):
    return await cv_service.delete_cv(candidate_id)


@router.post("/rfps")
async def create_rfp(file: UploadFile | None = File(default=None), text: str | None = Form(default=None)):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide file or text")
    return await rfp_service.create_rfp(file=file, text=text)


@router.get("/rfps")
async def list_rfps():
    return await rfp_service.list_rfps()


@router.get("/rfps/{rfp_id}")
async def get_rfp(rfp_id: str):
    rfp = await rfp_service.get_rfp(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return rfp


@router.post("/match/run")
async def run_match(payload: dict):
    rfp_id = payload.get("rfp_id")
    top_n = int(payload.get("top_n", 10))
    debug = bool(payload.get("debug", False))
    result = await match_service.run(rfp_id=rfp_id, top_n=top_n, debug=debug)
    if not result:
        raise HTTPException(status_code=404, detail="RFP not found")
    return result


@router.get("/match/run/{run_id}")
async def get_match_run(run_id: str):
    run = await match_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
