from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/github")
async def github_webhook(request: Request, x_hub_signature_256: Optional[str] = Header(default=None)):
    try:
        _ = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    return {"ok": True}


