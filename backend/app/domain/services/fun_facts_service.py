from openai import OpenAI
from fastapi import HTTPException
from app.core.config import settings
from app.domain.models.fun_facts import FunFactsResult
from app.domain.services.pokemon_service import get_pokemon

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a Pokédex enhancement AI.

You will receive a Pokémon name and you will return:
1. A short flavor-style summary (not more than 3 sentences)
2. 4–6 fun facts
3. Each fun fact must include:
   - fact (short)
   - relevance (why this is interesting or important)

Return a JSON object following this structure:
{
  "pokemon": "name",
  "summary": "...",
  "fun_facts": [
      {"fact": "...", "relevance": "..."}
  ]
}
"""

def get_fun_facts(pokemon_name: str):
    # validate Pokémon
    try:
        poke = get_pokemon(pokemon_name)
    except Exception:
        raise HTTPException(404, "Pokémon not found")

    # Send structured request
    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Pokemon: {poke.name}"},
        ],
        text_format=FunFactsResult
    )

    parsed = response.output_parsed

    return {
        "pokemon": parsed.pokemon,
        "summary": parsed.summary,
        "fun_facts": parsed.fun_facts
    }