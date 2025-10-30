from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from .database import execute, fetch_one


async def create_challenge(data: Dict[str, Any]) -> Dict[str, Any]:
    row = await fetch_one(
        """
        INSERT INTO challenges (
            title, description, instructions, seed_github_url,
            start_window_hours, complete_window_hours, email_subject, email_body,
            seed_repo_name, seed_repo_id, seed_is_template, seed_main_head_sha, last_seed_sync_at, created_by
        ) VALUES (
            :title, :description, :instructions, :seed_github_url,
            :start_window_hours, :complete_window_hours, :email_subject, :email_body,
            :seed_repo_name, :seed_repo_id, :seed_is_template, :seed_main_head_sha, now(), :created_by
        ) RETURNING id, seed_main_head_sha
        """,
        data,
    )
    assert row is not None
    return row


async def upsert_candidate(email: str, name: Optional[str]) -> str:
    row = await fetch_one(
        """
        INSERT INTO candidates (email, name)
        VALUES (:email, :name)
        ON CONFLICT (email) DO UPDATE SET name = COALESCE(EXCLUDED.name, candidates.name)
        RETURNING id
        """,
        {"email": email, "name": name},
    )
    assert row is not None
    return row["id"]


async def create_invite(challenge_id: str, candidate_id: str, start_deadline_at: datetime) -> Dict[str, Any]:
    row = await fetch_one(
        """
        INSERT INTO challenge_invites (challenge_id, candidate_id, start_deadline_at)
        VALUES (:challenge_id, :candidate_id, :start_deadline_at)
        RETURNING id, start_token
        """,
        {"challenge_id": challenge_id, "candidate_id": candidate_id, "start_deadline_at": start_deadline_at},
    )
    assert row is not None
    return row


async def get_invite_by_token(token: str) -> Optional[Dict[str, Any]]:
    return await fetch_one(
        """
        SELECT ai.*, c.title, c.description, c.instructions, c.complete_window_hours, c.start_window_hours,
               c.seed_repo_name, c.seed_main_head_sha
        FROM challenge_invites ai
        JOIN challenges c ON c.id = ai.challenge_id
        WHERE ai.start_token::text = :token
        """,
        {"token": token},
    )


async def mark_invite_started(invite_id: str) -> None:
    await execute(
        """
        UPDATE challenge_invites
        SET started_at = now(), complete_deadline_at = now() + (SELECT make_interval(hours := c.complete_window_hours) FROM challenges c WHERE c.id = challenge_id), status = 'started'
        WHERE id = :invite_id AND status = 'pending'
        """,
        {"invite_id": invite_id},
    )


async def update_invite_repo(invite_id: str, values: Dict[str, Any]) -> None:
    await execute(
        """
        UPDATE challenge_invites SET
            candidate_repo_id = :candidate_repo_id,
            candidate_repo_name = :candidate_repo_name,
            candidate_repo_html_url = :candidate_repo_html_url,
            candidate_repo_clone_url = :candidate_repo_clone_url,
            pinned_seed_sha = :pinned_seed_sha
        WHERE id = :invite_id
        """,
        {**values, "invite_id": invite_id},
    )


async def get_invite(invite_id: str) -> Optional[Dict[str, Any]]:
    return await fetch_one(
        """
        SELECT ai.*, c.title, c.description, c.instructions, c.complete_window_hours,
               c.seed_repo_name, c.seed_main_head_sha
        FROM challenge_invites ai
        JOIN challenges c ON c.id = ai.challenge_id
        WHERE ai.id = :invite_id
        """,
        {"invite_id": invite_id},
    )


async def mark_invite_submitted(invite_id: str, final_commit_sha: str) -> None:
    await execute(
        """
        UPDATE challenge_invites SET status = 'submitted', submitted_at = now(), final_commit_sha = :final_commit_sha
        WHERE id = :invite_id
        """,
        {"invite_id": invite_id, "final_commit_sha": final_commit_sha},
    )


async def get_challenge(challenge_id: str) -> Optional[Dict[str, Any]]:
    return await fetch_one(
        """
        SELECT * FROM challenges WHERE id = :id
        """,
        {"id": challenge_id},
    )


