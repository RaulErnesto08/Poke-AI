from pydantic import BaseModel
from typing import List

class FunFact(BaseModel):
    fact: str
    relevance: str

class FunFactsResult(BaseModel):
    pokemon: str
    summary: str
    fun_facts: List[FunFact]