import base64
import time
from typing import Any, Dict, Optional, Tuple

import httpx
import jwt

from .config import get_settings


class GitHubAppClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._api = "https://api.github.com"

    def _app_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 9 * 60,
            "iss": self.settings.github_app_id,
        }
        private_key = self._load_private_key()
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token if isinstance(token, str) else token.decode()

    def _load_private_key(self) -> str:
        key = self.settings.github_private_key
        if "BEGIN RSA PRIVATE KEY" in key or "BEGIN PRIVATE KEY" in key:
            return key
        try:
            decoded = base64.b64decode(key).decode()
            return decoded
        except Exception:
            return key

    async def list_installations(self) -> list[Dict]:
        """List all installations for this GitHub App."""
        app_jwt = self._app_jwt()
        url = f"{self._api}/app/installations"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"})
            resp.raise_for_status()
            installations = resp.json()
            # GitHub returns a list directly
            return installations if isinstance(installations, list) else []

    async def validate_installation_id(self, installation_id: Optional[str] = None) -> bool:
        """Check if the given installation ID (or configured one) exists and is accessible."""
        target_id = installation_id or self.settings.github_installation_id
        try:
            installations = await self.list_installations()
            for installation in installations:
                if str(installation.get("id")) == str(target_id):
                    return True
            return False
        except Exception:
            return False

    async def get_installation_details(self, installation_id: Optional[str] = None) -> Optional[Dict]:
        """Get detailed information about a specific installation."""
        target_id = installation_id or self.settings.github_installation_id
        try:
            installations = await self.list_installations()
            for installation in installations:
                if str(installation.get("id")) == str(target_id):
                    return installation
            return None
        except Exception:
            return None

    async def validate_installation_access(self, installation_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate that installation has 'all' repository access (required for org repo creation).
        Returns (is_valid, error_message).
        """
        installation = await self.get_installation_details(installation_id)
        if not installation:
            return False, f"Installation ID '{installation_id or self.settings.github_installation_id}' not found"
        
        repository_selection = installation.get("repository_selection")
        if repository_selection != "all":
            available_selection = repository_selection or "selected"
            return False, (
                f"Installation is set to '{available_selection}' repository access, but 'all' access is required "
                f"to create repositories via organization endpoints. Please reinstall the GitHub App with "
                f"'All repositories' access in your organization/user settings."
            )
        
        # Check permissions - ensure Administration permission is present
        permissions = installation.get("permissions", {})
        admin_permission = permissions.get("administration")
        if admin_permission != "write":
            return False, (
                f"GitHub App installation has Administration permission set to '{admin_permission}', "
                f"but 'write' access is required to create repositories. Please update the GitHub App "
                f"permissions and reinstall the app."
            )
        
        return True, None

    async def _installation_token(self, repositories: Optional[list[str]] = None) -> Dict:
        app_jwt = self._app_jwt()
        url = f"{self._api}/app/installations/{self.settings.github_installation_id}/access_tokens"
        data: Dict = {}
        if repositories:
            data["repositories"] = repositories
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"}, json=data)
            if resp.status_code == 404:
                # Installation not found - try to list available installations
                try:
                    installations = await self.list_installations()
                    installation_ids = [str(inst.get("id")) for inst in installations]
                    if installation_ids:
                        error_msg = (
                            f"GitHub App installation ID '{self.settings.github_installation_id}' not found. "
                            f"Available installation IDs: {', '.join(installation_ids)}. "
                            f"Please update GITHUB_INSTALLATION_ID environment variable or config."
                        )
                    else:
                        error_msg = (
                            f"GitHub App installation ID '{self.settings.github_installation_id}' not found. "
                            f"No installations found for this GitHub App. "
                            f"Please install the GitHub App on your organization/user account."
                        )
                except Exception as e:
                    error_msg = (
                        f"GitHub App installation ID '{self.settings.github_installation_id}' not found (404). "
                        f"Could not list available installations: {str(e)}. "
                        f"Please verify the installation ID is correct and the GitHub App is properly installed."
                    )
                raise ValueError(error_msg)
            resp.raise_for_status()
            return resp.json()

    async def get_installation_token_string(self, repositories: Optional[list[str]] = None) -> str:
        token_obj = await self._installation_token(repositories)
        return token_obj["token"]

    async def create_repo_from_template(self, template_repo: str, new_name: str, private: bool = True) -> Dict:
        # template_repo format: org/name
        token = await self.get_installation_token_string()
        url = f"{self._api}/repos/{template_repo}/generate"
        payload = {"owner": self.settings.github_org, "name": new_name, "private": private, "include_all_branches": False}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def repo_exists(self, repo_full: str) -> bool:
        """Check if a repository exists."""
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return True
            elif resp.status_code == 404:
                return False
            else:
                # Some other error - raise it
                resp.raise_for_status()
                return False

    async def _check_if_org_or_user(self, identifier: str) -> str:
        """Check if identifier is an org or user. Returns 'org' or 'user'."""
        token = await self.get_installation_token_string()
        # Try org endpoint first
        org_url = f"{self._api}/orgs/{identifier}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(org_url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})
            if resp.status_code == 200:
                return "org"
            elif resp.status_code == 404:
                # Try user endpoint
                user_url = f"{self._api}/users/{identifier}"
                resp = await client.get(user_url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})
                if resp.status_code == 200:
                    return "user"
                else:
                    raise ValueError(f"'{identifier}' is neither a valid organization nor a user")
            else:
                resp.raise_for_status()
                return "org"  # Default assumption

    async def create_org_repo(self, name: str, private: bool = True, description: Optional[str] = None, auto_init: bool = False) -> Dict:
        """Create a repository. Uses App token for orgs; supports PAT for personal user accounts."""
        # Determine if github_org is actually an org or a user
        account_type = await self._check_if_org_or_user(self.settings.github_org)

        # Choose endpoint and auth
        if account_type == "user" and self.settings.github_pat:
            url = f"{self._api}/user/repos"
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            url = f"{self._api}/orgs/{self.settings.github_org}/repos" if account_type == "org" else f"{self._api}/user/repos"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

        payload: Dict[str, Any] = {"name": name, "private": private}
        if description:
            payload["description"] = description
        # Optionally ask GitHub to initialize the repository (creates default README)
        payload["auto_init"] = auto_init
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            # Provide better error messages
            if resp.status_code == 422:
                error_data = resp.json()
                error_msg = error_data.get("message", "Unprocessable entity")
                if "name already exists" in error_msg.lower() or "already exists" in error_msg.lower():
                    raise ValueError(f"Repository {self.settings.github_org}/{name} already exists")
                else:
                    raise ValueError(f"Cannot create repository: {error_msg}")
            elif resp.status_code == 403:
                error_data = resp.json() if resp.content else {}
                error_msg = error_data.get("message", "Forbidden")
                
                # Try to get more specific information about why access was denied
                detailed_error = f"GitHub App does not have permission to create repositories: {error_msg}"
                
                # Check if it's a repository access level issue
                try:
                    is_valid, access_error = await self.validate_installation_access()
                    if not is_valid and access_error:
                        detailed_error = access_error
                except Exception:
                    # If validation fails, provide general guidance
                    detailed_error += (
                        ". Common causes: "
                        "1) Installation is set to 'Only select repositories' instead of 'All repositories' - "
                        "you must reinstall the app with 'All repositories' access. "
                        "2) Permissions were updated but installation wasn't re-authorized - "
                        "reinstall the app after changing permissions. "
                        "3) Missing 'Administration: Write' permission - ensure this is set to 'Read & write'."
                    )
                
                raise PermissionError(detailed_error)
            elif resp.status_code == 404:
                error_data = resp.json() if resp.content else {}
                error_msg = error_data.get("message", "Not found")
                raise ValueError(f"Cannot find organization or user '{self.settings.github_org}': {error_msg}. Please check the GitHub App has access to this account.")
            resp.raise_for_status()
            return resp.json()

    async def start_repo_import(self, repo_full: str, vcs_url: str, vcs: str = "git") -> Dict:
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}/import"
        payload = {"vcs": vcs, "vcs_url": vcs_url}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.put(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_repo_import_status(self, repo_full: str) -> Dict:
        """Get the current status of a repository import."""
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}/import"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def wait_for_import_completion(self, repo_full: str, max_wait_seconds: int = 300, poll_interval: int = 5) -> Dict:
        """Wait for a repository import to complete, polling until done or timeout."""
        import asyncio
        elapsed = 0
        while elapsed < max_wait_seconds:
            status = await self.get_repo_import_status(repo_full)
            status_text = status.get("status", "unknown").lower()
            
            if status_text == "complete":
                return status
            elif status_text in ("failed", "error", "auth_failed"):
                error_msg = status.get("message", "Unknown error")
                raise ValueError(f"Repository import failed: {error_msg}")
            elif status_text in ("importing", "detecting", "mapping"):
                # Still in progress, wait and check again
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            else:
                # Unknown status, wait a bit and retry
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
        
        raise TimeoutError(f"Repository import did not complete within {max_wait_seconds} seconds")

    async def mark_repo_as_template(self, repo_full: str) -> None:
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.patch(url, headers=headers, json={"is_template": True})
            resp.raise_for_status()

    async def set_default_branch(self, repo_full: str, branch: str = "main") -> None:
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.patch(url, headers=headers, json={"default_branch": branch})
            resp.raise_for_status()

    async def archive_repo(self, repo_full: str) -> None:
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.patch(url, headers=headers, json={"archived": True})
            resp.raise_for_status()

    async def get_branch_head_sha(self, repo_full: str, branch: str = "main") -> str:
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}/branches/{branch}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()["commit"]["sha"]

    def tokenized_clone_url(self, repo_full: str, install_token: str) -> str:
        return f"https://x-access-token:{install_token}@github.com/{repo_full}.git"

    async def get_tree(self, repo_full: str, sha: str) -> Dict:
        owner = repo_full.split("/", 1)[0]
        account_type = await self._check_if_org_or_user(self.settings.github_org)
        if account_type == "user" and owner == self.settings.github_org and self.settings.github_pat:
            headers = {"Authorization": f"token {self.settings.github_pat}", "Accept": "application/vnd.github+json"}
        else:
            token = await self.get_installation_token_string()
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        url = f"{self._api}/repos/{repo_full}/git/trees/{sha}?recursive=1"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()


