from openai import OpenAI
from fastapi import HTTPException
from app.core.config import settings
from app.domain.services.pokemon_service import get_pokemon
from app.domain.repositories.collection_repository import CollectionRepository
from sqlalchemy.orm import Session

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a Pokémon expert. You will receive a list of Pokémon owned by a user.

Your tasks:
1. Analyze type distribution.
2. Identify weaknesses and missing synergies.
3. Recommend 3–5 Pokémon that would improve the user's team.

For each recommended Pokémon include:
- name (English)
- reason (short explanation)

Return as a structured JSON object:
{
  "summary": "...",
  "recommendations": [
    {"name": "Example", "reason": "..." }
  ]
}
"""

def recommend_for_user(db: Session, user_id: int):
    # Obtain user's collection
    repo = CollectionRepository(db)
    items = repo.list_ids(user_id)

    if not items:
        raise HTTPException(400, "You must have at least 1 Pokémon in your collection")

    # Load full details for AI
    pokemon_list = []
    for m in items[:20]:
        try:
            p = get_pokemon(m)
            pokemon_list.append({
                "id": p.id,
                "name": p.name,
                "types": p.types,
                "stats": p.stats
            })
        except Exception:
            continue

    # Build content for AI
    content = {
        "owned": pokemon_list
    }

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(content)},
        ]
    )

    output_text = response.output_text

    # We expect JSON, but if AI outputs Markdown we try to extract JSON
    import json
    try:
        parsed = json.loads(output_text)
    except Exception:
        # Attempt to fix markdown formatting
        cleaned = output_text.strip().replace("```json", "").replace("```", "")
        parsed = json.loads(cleaned)

    # Convert AI names to real Pokémon info
    results = []
    for rec in parsed.get("recommendations", []):
        name = rec["name"]
        reason = rec.get("reason", "")
        try:
            poke = get_pokemon(name)
            results.append({
                "id": poke.id,
                "name": poke.name,
                "sprite": poke.sprite,
                "types": poke.types,
                "reason": reason
            })
        except Exception:
            # fallback only with name
            results.append({
                "id": None,
                "name": name,
                "sprite": None,
                "types": [],
                "reason": reason
            })

    return {
        "summary": parsed.get("summary", ""),
        "recommendations": results
    }