from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.infra.orm import CollectionItem

class CollectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, user_id: int, pokemon_id: int) -> CollectionItem:
        item = CollectionItem(user_id=user_id, pokemon_id=pokemon_id)
        self.db.add(item)
        self.db.flush()  # para obtener id
        self.db.refresh(item)
        return item

    def exists(self, user_id: int, pokemon_id: int) -> bool:
        q = select(CollectionItem.id).where(
            CollectionItem.user_id == user_id,
            CollectionItem.pokemon_id == pokemon_id
        )
        return self.db.execute(q).scalar() is not None

    def remove(self, user_id: int, pokemon_id: int) -> int:
        q = delete(CollectionItem).where(
            CollectionItem.user_id == user_id,
            CollectionItem.pokemon_id == pokemon_id
        )
        res = self.db.execute(q)
        return res.rowcount or 0

    def list_ids(self, user_id: int) -> List[int]:
        q = select(CollectionItem.pokemon_id).where(
            CollectionItem.user_id == user_id
        ).order_by(CollectionItem.created_at.desc(), CollectionItem.id.desc())
        return [row[0] for row in self.db.execute(q).all()]