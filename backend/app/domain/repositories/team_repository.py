from sqlalchemy.orm import Session

from app.infra.orm import Team, TeamMember


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------
    # Teams
    # ----------------------------
    def create_team(self, user_id: int, name: str) -> Team:
        t = Team(user_id=user_id, name=name)
        self.db.add(t)
        self.db.flush()
        self.db.refresh(t)
        return t

    def list_by_user(self, user_id: int) -> list[Team]:
        return (
            self.db.query(Team)
            .filter(Team.user_id == user_id)
            .order_by(Team.created_at.desc())
            .all()
        )

    def get_team(self, team_id: int) -> Team | None:
        return (
            self.db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

    def delete_team(self, team_id: int) -> None:
        self.db.query(Team).filter(Team.id == team_id).delete()

    # ----------------------------
    # Members
    # ----------------------------
    def member_exists(self, team_id: int, pokemon_id: int) -> bool:
        return (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.pokemon_id == pokemon_id,
            )
            .first()
            is not None
        )

    def add_member(self, team_id: int, pokemon_id: int) -> TeamMember:
        m = TeamMember(team_id=team_id, pokemon_id=pokemon_id)
        self.db.add(m)
        self.db.flush()
        self.db.refresh(m)
        return m

    def remove_member(self, team_id: int, pokemon_id: int) -> bool:
        q = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.pokemon_id == pokemon_id,
            )
        )
        if q.first():
            q.delete()
            return True
        return False