from pydantic import BaseModel
from typing import List, Optional


# --- AI structured output model ---
class AutoTeamAIItem(BaseModel):
    name: str


class AutoTeamAIResponse(BaseModel):
    summary: str
    team: List[AutoTeamAIItem]


# --- Final enriched models returned to frontend ---
class AutoTeamMember(BaseModel):
    id: int
    reason: str


class AutoTeamResult(BaseModel):
    summary: str
    team: List[AutoTeamMember]