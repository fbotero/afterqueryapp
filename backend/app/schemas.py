from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, Union


class ChallengeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    seed_github_url: Union[HttpUrl, str]
    start_window_hours: int
    complete_window_hours: int
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    slug: str


class InviteCreate(BaseModel):
    candidate_email: str
    candidate_name: Optional[str] = None


class StartView(BaseModel):
    title: str
    description: Optional[str]
    instructions: Optional[str]
    start_deadline_at: datetime
    complete_window_hours: int
    branch: str = "main"


class StartResponse(BaseModel):
    clone_url: str
    repo_html_url: str
    branch: str = "main"


class RefreshResponse(BaseModel):
    clone_url: str


