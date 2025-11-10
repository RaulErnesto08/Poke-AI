import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")  # Token fijo desde .env

if not ACCESS_TOKEN:
    print("⚠️ Warning: ACCESS_TOKEN not set in .env (auth endpoints will fail)")

# MCP instance
mcp = FastMCP(
    name="pokeapi-mcp",
    instructions="Tools for interacting with the PokeAPI backend.",
)


# ---- Helper ----
async def call_api(method: str, endpoint: str, **kwargs):
    """Generic helper for making authenticated requests."""
    url = f"{API_URL}{endpoint}"

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except Exception as e:
            return {"error": str(e)}


# =========================================================
# POKEDEX TOOLS
# =========================================================

@mcp.tool()
async def search_pokemon(query: str) -> str:
    """Search Pokémon by name."""
    data = await call_api("GET", f"/pokedex/search?query={query}")
    return str(data)


@mcp.tool()
async def lookup_pokemon(name_or_id: str) -> str:
    """Get Pokémon full detail."""
    data = await call_api("GET", f"/pokedex/look/{name_or_id}")
    return str(data)


@mcp.tool()
async def random_pokemon() -> str:
    """Get a random Pokémon."""
    data = await call_api("GET", "/pokedex/random")
    return str(data)


# =========================================================
# COLLECTION TOOLS
# =========================================================

@mcp.tool()
async def list_collection() -> str:
    """List collection items."""
    data = await call_api("GET", "/collection")
    return str(data)


@mcp.tool()
async def add_to_collection(pokemon_id: int) -> str:
    """Add Pokémon to collection."""
    data = await call_api("POST", f"/collection/add/{pokemon_id}")
    return str(data)


@mcp.tool()
async def remove_from_collection(pokemon_id: int) -> str:
    """Remove Pokémon from collection."""
    data = await call_api("DELETE", f"/collection/remove/{pokemon_id}")
    return str(data)


# =========================================================
# TEAM TOOLS
# =========================================================

@mcp.tool()
async def list_teams() -> str:
    """List all teams."""
    data = await call_api("GET", "/teams")
    return str(data)


@mcp.tool()
async def create_team(name: str) -> str:
    """Create a team with a name."""
    data = await call_api("POST", "/teams", json={"name": name})
    return str(data)


@mcp.tool()
async def get_team(team_id: int) -> str:
    """Get team detail."""
    data = await call_api("GET", f"/teams/{team_id}")
    return str(data)


@mcp.tool()
async def rename_team(team_id: int, new_name: str) -> str:
    """Rename a team."""
    data = await call_api("PATCH", f"/teams/{team_id}/rename", json={"new_name": new_name})
    return str(data)


@mcp.tool()
async def add_to_team(team_id: int, pokemon_id: int) -> str:
    """Add Pokémon to team."""
    data = await call_api("POST", f"/teams/{team_id}/add/{pokemon_id}")
    return str(data)


@mcp.tool()
async def remove_from_team(team_id: int, pokemon_id: int) -> str:
    """Remove Pokémon from team."""
    data = await call_api("DELETE", f"/teams/{team_id}/remove/{pokemon_id}")
    return str(data)


@mcp.tool()
async def delete_team(team_id: int) -> str:
    """Delete a team."""
    data = await call_api("DELETE", f"/teams/{team_id}")
    return str(data)


# =========================================================
# AI TOOLS
# =========================================================

@mcp.tool()
async def ai_compare(a: str, b: str) -> str:
    """AI analysis comparing two Pokémon."""
    data = await call_api("POST", "/ai/compare", json={"pokemon_a": a, "pokemon_b": b})
    return str(data)


@mcp.tool()
async def ai_recommendations() -> str:
    """AI recommendations based on collection."""
    data = await call_api("POST", "/ai/recommendations")
    return str(data)


@mcp.tool()
async def ai_auto_team() -> str:
    """AI auto team builder."""
    data = await call_api("POST", "/ai/auto-team")
    return str(data)


@mcp.tool()
async def ai_fun_facts(name_or_id: str) -> str:
    """AI-generated curiosities."""
    data = await call_api("GET", f"/ai/fun-facts/{name_or_id}")
    return str(data)


# =========================================================
# Utility
# =========================================================

@mcp.tool()
async def healthcheck() -> str:
    """Simple health check."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(API_URL)
        return f"✅ Backend reachable: {API_URL}"
    except Exception as e:
        return f"❌ Backend unreachable: {e}"


# =========================================================
# RUN MCP
# =========================================================

if __name__ == "__main__":
    mcp.run()