from typing import List
from pydantic import BaseModel

class TeamCreateDTO(BaseModel):
    name: str

class TeamRenameDTO(BaseModel):
    name: str

class TeamMemberDTO(BaseModel):
    id: int
    name: str
    sprite: str | None = None
    types: List[str] = []

class TeamSummaryDTO(BaseModel):
    id: int
    name: str
    count: int
    created_at: str

class TeamDetailDTO(BaseModel):
    id: int
    name: str
    count: int
    members: List[TeamMemberDTO]