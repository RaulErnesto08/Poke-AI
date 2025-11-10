from pydantic import BaseModel
from typing import List


class AICandidate(BaseModel):
    name: str
    confidence: float


class VisionIdentifyResult(BaseModel):
    primary_name: str
    candidates: List[AICandidate]
    rationale: str