from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..schemas import ChallengeCreate, InviteCreate
from ..database import fetch_one
from ..services import AssessmentService, EmailService
from ..repo import create_challenge, upsert_candidate, create_invite as repo_create_invite, get_invite, get_challenge

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/challenges")
async def create_challenge_handler(body: ChallengeCreate) -> Dict[str, Any]:
    svc = AssessmentService()
    import logging
    logger = logging.getLogger(__name__)
    
    repo_setup_warnings = []
    try:
        is_valid = await svc.gh.validate_installation_id()
        if not is_valid:
            try:
                installations = await svc.gh.list_installations()
                installation_ids = [str(inst.get("id")) for inst in installations]
                if installation_ids:
                    warning_msg = (
                        f"GitHub App installation ID '{svc.settings.github_installation_id}' is invalid. "
                        f"Available installation IDs: {', '.join(installation_ids)}. "
                        f"Repository setup will be skipped. Please update GITHUB_INSTALLATION_ID environment variable."
                    )
                else:
                    warning_msg = (
                        f"GitHub App installation ID '{svc.settings.github_installation_id}' is invalid. "
                        f"No installations found for this GitHub App. Repository setup will be skipped."
                    )
                logger.warning(warning_msg)
                repo_setup_warnings.append(warning_msg)
            except Exception as list_error:
                warning_msg = f"Could not validate GitHub App installation: {str(list_error)}. Repository setup will be skipped."
                logger.warning(warning_msg)
                repo_setup_warnings.append(warning_msg)
        else:
            access_valid, access_error = await svc.gh.validate_installation_access()
            if not access_valid:
                warning_msg = f"GitHub App installation access validation failed: {access_error}. Repository setup may fail."
                logger.warning(warning_msg)
                repo_setup_warnings.append(warning_msg)
    except Exception as e:
        warning_msg = f"Could not validate GitHub App installation: {e}. Repository setup will be skipped."
        logger.warning(warning_msg)
        repo_setup_warnings.append(warning_msg)
    
    has_seed_url = bool(str(body.seed_github_url).strip())
    default_seed_url = "https://github.com/derijk/base"
    effective_seed_url = str(body.seed_github_url).strip() if has_seed_url else default_seed_url
    seed_repo_name = f"challenges-{body.slug}-seed"
    seed_repo_full = f"{svc.settings.github_org}/{seed_repo_name}"
    
    repo_exists = False
    try:
        repo_exists = await svc.gh.repo_exists(seed_repo_full)
        if repo_exists:
            logger.info(f"Repository {seed_repo_full} already exists")
        else:
            logger.info(f"Repository {seed_repo_full} does not exist, creating...")
            repo_result = await svc.gh.create_org_repo(seed_repo_name, private=False, description=f"Seed for challenge {body.slug}")
            logger.info(f"Created new repository: {seed_repo_full}")
            repo_exists = True
    except ValueError as e:
        error_str = str(e)
        if "already exists" in error_str.lower():
            logger.info(f"Repository {seed_repo_full} already exists, will use it")
            repo_exists = True
        else:
            warning_msg = f"Could not create repository {seed_repo_full}: {error_str}. Repository setup will be incomplete."
            logger.warning(warning_msg)
            repo_setup_warnings.append(warning_msg)
            repo_exists = False
    except PermissionError as e:
        # Permission error - log but continue
        warning_msg = f"Permission error creating repository: {str(e)}. Repository setup will be incomplete. Please check GitHub App permissions."
        logger.warning(warning_msg)
        repo_setup_warnings.append(warning_msg)
        repo_exists = False
    except Exception as e:
        # Any other error - log but continue
        warning_msg = f"Failed to set up repository {seed_repo_full}: {str(e)}. Repository setup will be incomplete."
        logger.warning(warning_msg)
        repo_setup_warnings.append(warning_msg)
        repo_exists = False
    
    # Step 2: Repo content setup: import if a seed URL is provided, otherwise ensure README via auto-init
    head_sha = None
    repo_setup_complete = False

    if repo_exists:
        if True:  # always import from effective_seed_url
            # Import flow from provided seed URL
            import_url = effective_seed_url
            if not import_url.endswith('.git'):
                import_url = f"{import_url}.git" if not import_url.endswith('/') else f"{import_url[:-1]}.git"
            try:
                logger.info(f"Starting import of {import_url} into {seed_repo_full}")
                import_status = await svc.gh.start_repo_import(seed_repo_full, import_url)
                logger.info(f"Import started: {import_status}")
                logger.info(f"Waiting for import to complete...")
                await svc.gh.wait_for_import_completion(seed_repo_full, max_wait_seconds=300)
                logger.info(f"Import completed successfully")
                try:
                    await svc.gh.set_default_branch(seed_repo_full, "main")
                    logger.info(f"Set default branch to main")
                except Exception as e:
                    logger.info(f"Default branch might already be main: {e}")
                try:
                    await svc.gh.mark_repo_as_template(seed_repo_full)
                    logger.info(f"Marked repository as template")
                except Exception as e:
                    logger.warning(f"Failed to mark as template: {e}")
                try:
                    head_sha = await svc.gh.get_branch_head_sha(seed_repo_full, "main")
                    logger.info(f"Got branch head SHA: {head_sha[:8]}...")
                    repo_setup_complete = True
                except Exception as e:
                    warning_msg = f"Could not get branch head SHA: {e}"
                    logger.warning(warning_msg)
                    repo_setup_warnings.append(warning_msg)
            except Exception as e:
                error_detail = str(e)
                warning_msg = f"Failed to complete GitHub repo setup for {seed_repo_full}: {error_detail}"
                logger.warning(warning_msg)
                repo_setup_warnings.append(warning_msg)
                if "import" in error_detail.lower() or "422" in error_detail or "empty" in error_detail.lower():
                    logger.warning(f"Import failed. Repository must be empty to import. Error: {error_detail}")
    else:
        logger.info(f"Skipping repository setup since repository does not exist or could not be created")

    row = await create_challenge(
        {
            "title": body.title,
            "description": body.description,
            "instructions": body.instructions,
            "seed_github_url": str(body.seed_github_url),
            "start_window_hours": body.start_window_hours,
            "complete_window_hours": body.complete_window_hours,
            "email_subject": body.email_subject,
            "email_body": body.email_body,
            "seed_repo_name": seed_repo_full,
            "seed_repo_id": None,
        "seed_is_template": True if has_seed_url else False,
            "seed_main_head_sha": head_sha,
            "created_by": None,
        }
    )
    
    response = {
        "challenge": {
            "id": row["id"],
            "seed_main_head_sha": row["seed_main_head_sha"],
            "seed_repo": seed_repo_full
        }
    }
    
    # Include warnings if repository setup had issues (non-blocking)
    if repo_setup_warnings:
        response["warnings"] = repo_setup_warnings
        response["repo_setup_status"] = "incomplete" if not repo_setup_complete else "partial"
    else:
        response["repo_setup_status"] = "complete" if repo_setup_complete else "not_attempted"
    
    return response


@router.post("/challenges/{challenge_id}/invites")
async def create_invite(challenge_id: str, body: InviteCreate) -> Dict[str, Any]:
    # Calculate start deadline (use default 72h if not stored). For MVP, 72h.
    start_deadline_at = datetime.now(tz=timezone.utc) + timedelta(hours=72)
    candidate_id = await upsert_candidate(body.candidate_email, body.candidate_name)
    invite = await repo_create_invite(challenge_id, candidate_id, start_deadline_at)
    start_token = invite["start_token"]
    start_link = f"/challenges/{challenge_id}/setup?token={start_token}"

    email_service = EmailService()
    # Try to send email, but don't fail the invite creation if email fails
    try:
        c = await get_challenge(challenge_id)
        seed_repo = c.get("seed_repo_name") if c else None
        app_base = AssessmentService().settings.app_base_url.rstrip('/')
        start_abs = f"{app_base}/challenges/{challenge_id}/setup?token={start_token}"
        seed_link = f"https://github.com/{seed_repo}" if seed_repo else None
        html = "<p>Please start your challenge here: <a href='{}'>Start</a></p>".format(start_abs)
        if seed_link:
            html += "<p>Challenge repository (read-only): <a href='{}'>{}</a></p>".format(seed_link, seed_link)
        await email_service.send(to_email=body.candidate_email, subject="Your Coding Challenge", html=html)
    except Exception as exc:  # pragma: no cover (network)
        # Log the error but don't fail the invite creation
        # The invite was already created in the database, so we should return success
        # In production, you might want to log this to a monitoring service
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to send invitation email to {body.candidate_email}: {exc}")
        # Return a warning in the response instead of failing
        return {
            "invite": {
                "candidate": body.candidate_email,
                "start_link": start_link,
                "email_sent": False,
                "warning": f"Invite created but email failed to send: {str(exc)}"
            }
        }

    return {"invite": {"candidate": body.candidate_email, "start_link": start_link}}


@router.get("/challenges/{challenge_id}/preview")
async def preview_challenge(challenge_id: str) -> Dict[str, Any]:
    # Minimal placeholder: return redacted commands
    return {"preview": {"start_page": {"title": "Challenge", "branch": "main", "instructions": "Follow the README"}, "git_commands": {"clone": "git clone https://x-access-token:<REDACTED>@github.com/org/repo.git", "push": "git push origin main"}}}


@router.get("/challenges/{challenge_id}")
async def get_challenge_detail(challenge_id: str) -> Dict[str, Any]:
    c = await get_challenge(challenge_id)
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    seed_repo = c.get("seed_repo_name")
    git_clone_url = f"https://github.com/{seed_repo}.git" if seed_repo else None
    return {
        "challenge": {
            "id": challenge_id,
            "title": c.get("title"),
            "description": c.get("description"),
            "instructions": c.get("instructions"),
            "seed_repo_name": seed_repo,
            "git_clone_url": git_clone_url,
        }
    }


@router.get("/invites/{invite_id}")
async def invite_detail(invite_id: str) -> Dict[str, Any]:
    inv = await get_invite(invite_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invite not found")
    return {"invite": inv}


@router.post("/invites/{invite_id}/follow-up")
async def send_follow_up(invite_id: str) -> Dict[str, Any]:
    inv = await get_invite(invite_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invite not found")
    email = EmailService()
    await email.send(inv["email"], "Follow-up Interview", "<p>We'd like to schedule a follow-up.</p>")
    return {"ok": True}


@router.get("/invites/{invite_id}/compare")
async def compare_invite(invite_id: str) -> Dict[str, Any]:
    inv = await get_invite(invite_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invite not found")
    svc = AssessmentService()
    seed_sha = inv["pinned_seed_sha"] or inv["seed_main_head_sha"]
    candidate_sha = inv["final_commit_sha"] or await svc.gh.get_branch_head_sha(inv["candidate_repo_name"], "main")
    seed_tree = await svc.gh.get_tree(inv["seed_repo_name"], seed_sha)
    cand_tree = await svc.gh.get_tree(inv["candidate_repo_name"], candidate_sha)
    seed_files = {t["path"] for t in seed_tree.get("tree", []) if t.get("type") == "blob"}
    cand_files = {t["path"] for t in cand_tree.get("tree", []) if t.get("type") == "blob"}
    added = sorted(list(cand_files - seed_files))
    removed = sorted(list(seed_files - cand_files))
    unchanged = sorted(list(seed_files & cand_files))
    return {"diff_summary": {"added": added, "removed": removed, "unchanged_count": len(unchanged)}}


@router.get("/db-health")
async def db_health() -> Dict[str, Any]:
    row = await fetch_one("SELECT 1 AS ok")
    return {"ok": bool(row and row.get("ok") == 1)}

