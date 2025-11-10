from openai import OpenAI
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.domain.repositories.collection_repository import CollectionRepository
from app.domain.services.pokemon_service import get_pokemon
from app.domain.models.auto_team import AutoTeamResult

client = OpenAI(api_key=settings.OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a Pokémon team-building expert.

You will receive a list of Pokémon IDs the user owns.

Your goal:
- Select the best 6 Pokémon from the owned list.
- Return only valid Pokémon IDs.
- The team must contain exactly 6 distinct Pokémon.
- IDs must be from the list the user owns.

Return only structured JSON:
{
  "summary": "...",
  "team": [
    {"id": 445, "reason": "..."},
    {"id": 130, "reason": "..."},
    {"id": 6,   "reason": "..."},
    {"id": 25,  "reason": "..."},
    {"id": 143, "reason": "..."},
    {"id": 65,  "reason": "..."}
  ]
}
"""


def build_auto_team(db: Session, user_id: int):
    repo = CollectionRepository(db)
    collection_ids = repo.list_ids(user_id)

    if not collection_ids:
        raise HTTPException(400, "Collection is empty. Cannot build a team.")

    # content sent to AI
    payload = {"owned_ids": collection_ids}

    # parse structured output directly
    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(payload)}
        ],
        text_format=AutoTeamResult
    )

    ai_result = response.output_parsed  # ✅ validated AutoTeamResult object

    # Post-process to fetch full Pokémon data
    full_team = []

    for member in ai_result.team:
        if member.id not in collection_ids:
            continue  # never trust 100% the model

        try:
            p = get_pokemon(member.id)
            full_team.append({
                "id": p.id,
                "name": p.name,
                "sprite": p.sprite,
                "types": p.types,
                "stats": p.stats,
                "reason": member.reason
            })
        except Exception:
            continue

    return {
        "summary": ai_result.summary,
        "team": full_team
    }