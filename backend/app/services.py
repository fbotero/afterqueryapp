import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from .config import get_settings
from .github_app import GitHubAppClient


class AssessmentService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.gh = GitHubAppClient()

    async def prepare_seed_repo(self, upstream_url: str, slug: str) -> Dict:
        seed_repo_full = f"{self.settings.github_org}/assessments-{slug}-seed"
        try:
            await self.gh.set_default_branch(seed_repo_full, "main")
        except Exception:
            pass
        head_sha = await self.gh.get_branch_head_sha(seed_repo_full, "main")
        return {"seed_repo_full": seed_repo_full, "seed_main_head_sha": head_sha}

    async def create_candidate_repo(self, seed_repo_full: str, assessment_slug: str) -> Dict:
        new_name = f"assessments-{assessment_slug}-candidate-{int(datetime.now(tz=timezone.utc).timestamp())}"
        created = await self.gh.create_repo_from_template(seed_repo_full, new_name)
        repo_full = f"{created['owner']['login']}/{created['name']}"
        head_sha = await self.gh.get_branch_head_sha(repo_full, "main")
        token = await self.gh.get_installation_token_string()
        clone_url = self.gh.tokenized_clone_url(repo_full, token)
        return {
            "repo_full": repo_full,
            "repo_id": created["id"],
            "html_url": created["html_url"],
            "clone_url": clone_url,
            "head_sha": head_sha,
        }

    async def archive_candidate_repo(self, repo_full: str) -> None:
        await self.gh.archive_repo(repo_full)

    async def issue_installation_token_url(self, repo_full: str) -> str:
        token = await self.gh.get_installation_token_string()
        return self.gh.tokenized_clone_url(repo_full, token)


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send(self, to_email: str, subject: str, html: str) -> Dict:
        import httpx

        from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
        
        payload = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.settings.resend_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
            )
            if resp.status_code == 403:
                error_detail = resp.json().get("message", "Forbidden") if resp.content else "Forbidden: Check API key and verified domain"
                raise ValueError(f"Resend API 403 Forbidden: {error_detail}. Make sure your API key is valid and the 'from' email is verified.")
            resp.raise_for_status()
            return resp.json()


