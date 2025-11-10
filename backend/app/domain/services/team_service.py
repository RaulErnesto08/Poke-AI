from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.repositories.collection_repository import CollectionRepository
from app.domain.repositories.team_repository import TeamRepository
from app.domain.services.pokemon_service import get_pokemon


def _team_to_detail(team) -> dict:
    """Convierte un objeto Team a su estructura detallada"""
    members_detailed = []

    for m in team.members:
        try:
            poke = get_pokemon(m.pokemon_id)
            members_detailed.append({
                "id": poke.id,
                "name": poke.name,
                "sprite": poke.sprite,
                "types": poke.types,
            })
        except Exception:
            members_detailed.append({
                "id": m.pokemon_id,
                "name": f"pokemon-{m.pokemon_id}",
                "sprite": None,
                "types": [],
            })

    return {
        "id": team.id,
        "name": team.name,
        "count": len(members_detailed),
        "members": members_detailed,
    }


def create_team(db: Session, user_id: int, name: str):
    if not name or not name.strip():
        raise HTTPException(400, "Name required")

    repo = TeamRepository(db)
    team = repo.create_team(user_id, name.strip())
    db.commit()

    # devolver estructura completa
    return _team_to_detail(team)


def list_teams(db: Session, user_id: int):
    repo = TeamRepository(db)
    teams = repo.list_by_user(user_id)

    return [
        {
            "id": t.id,
            "name": t.name,
            "count": len(t.members),
            "created_at": t.created_at.isoformat(),
        }
        for t in teams
    ]


def get_team(db: Session, user_id: int, team_id: int):
    repo = TeamRepository(db)
    team = repo.get_team(team_id)

    if not team or team.user_id != user_id:
        raise HTTPException(404, "Team not found")

    return _team_to_detail(team)


def rename_team(db: Session, user_id: int, team_id: int, new_name: str):
    repo = TeamRepository(db)
    team = repo.get_team(team_id)

    if not team or team.user_id != user_id:
        raise HTTPException(404, "Team not found")

    if not new_name.strip():
        raise HTTPException(400, "Name required")

    team.name = new_name.strip()
    db.commit()

    return _team_to_detail(team)


def add_member(db: Session, user_id: int, team_id: int, pokemon_id: int):
    repo = TeamRepository(db)
    team = repo.get_team(team_id)

    if not team or team.user_id != user_id:
        raise HTTPException(404, "Team not found")

    # validar si está en collection
    collection_repo = CollectionRepository(db)
    if not collection_repo.exists(user_id, pokemon_id):
        raise HTTPException(400, "You must have this Pokémon in your collection first")

    if len(team.members) >= 6:
        raise HTTPException(400, "Team full (max 6 pokemon)")

    if repo.member_exists(team_id, pokemon_id):
        raise HTTPException(409, "Pokemon already in this team")

    repo.add_member(team_id, pokemon_id)
    db.commit()
    db.refresh(team)

    return _team_to_detail(team)


def remove_member(db: Session, user_id: int, team_id: int, pokemon_id: int):
    repo = TeamRepository(db)
    team = repo.get_team(team_id)

    if not team or team.user_id != user_id:
        raise HTTPException(404, "Team not found")

    deleted = repo.remove_member(team_id, pokemon_id)
    db.commit()

    if not deleted:
        raise HTTPException(404, "Pokemon not in this team")

    db.refresh(team)
    return _team_to_detail(team)


def delete_team(db: Session, user_id: int, team_id: int):
    repo = TeamRepository(db)
    team = repo.get_team(team_id)

    if not team or team.user_id != user_id:
        raise HTTPException(404, "Team not found")

    repo.delete_team(team_id)
    db.commit()

    return {"deleted": True}