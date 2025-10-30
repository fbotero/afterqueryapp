from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..schemas import RefreshResponse, StartResponse
from ..services import AssessmentService
from ..repo import get_invite_by_token, mark_invite_started, update_invite_repo, mark_invite_submitted

router = APIRouter(prefix="/api/candidate", tags=["candidate"])


@router.get("/start/{token}")
async def get_start_view(token: str) -> Dict[str, Any]:
    invite = await get_invite_by_token(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid token")
    return {
        "title": invite["title"],
        "description": invite["description"],
        "instructions": invite["instructions"],
        "branch": "main",
        "start_deadline_at": invite["start_deadline_at"],
        "complete_window_hours": invite["complete_window_hours"],
    }


@router.post("/start/{token}")
async def post_start(token: str) -> StartResponse:
    svc = AssessmentService()
    invite = await get_invite_by_token(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid token")
    if invite["status"] not in ("pending", "started"):
        raise HTTPException(status_code=400, detail="Invite not active")
    now = datetime.now(tz=timezone.utc)
    if now > invite["start_deadline_at"] and not invite.get("started_at"):
        raise HTTPException(status_code=400, detail="Start window expired")
    # Mark started (sets complete deadline)
    if not invite.get("started_at"):
        await mark_invite_started(invite["id"])

    seed_repo_full = invite["seed_repo_name"]
    slug = invite["assessment_id"][:8]
    created = await svc.create_candidate_repo(seed_repo_full, assessment_slug=slug)
    await update_invite_repo(
        invite_id=invite["id"],
        values={
            "candidate_repo_id": created["repo_id"],
            "candidate_repo_name": created["repo_full"],
            "candidate_repo_html_url": created["html_url"],
            "candidate_repo_clone_url": created["clone_url"],
            "pinned_seed_sha": invite["seed_main_head_sha"],
        },
    )
    return StartResponse(clone_url=created["clone_url"], repo_html_url=created["html_url"], branch="main")


@router.post("/refresh/{token}")
async def refresh_clone_url(token: str) -> RefreshResponse:
    invite = await get_invite_by_token(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid token")
    if invite["status"] != "started":
        raise HTTPException(status_code=400, detail="Not in progress")
    now = datetime.now(tz=timezone.utc)
    if invite["complete_deadline_at"] and now > invite["complete_deadline_at"]:
        raise HTTPException(status_code=400, detail="Assessment window expired")
    svc = AssessmentService()
    url = await svc.issue_installation_token_url(invite["candidate_repo_name"])  # repo_full
    return RefreshResponse(clone_url=url)


@router.post("/submit/{token}")
async def submit_assessment(token: str) -> Dict[str, Any]:
    invite = await get_invite_by_token(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid token")
    svc = AssessmentService()
    # Capture current head as final
    final_sha = await svc.gh.get_branch_head_sha(invite["candidate_repo_name"], "main")
    await mark_invite_submitted(invite["id"], final_sha)
    await svc.archive_candidate_repo(invite["candidate_repo_name"])
    return {"ok": True}


