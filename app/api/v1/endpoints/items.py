from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import DbSession, get_current_user
from app.repositories import item_repo
from app.schemas.common import Page
from app.schemas.item import ItemCreate, ItemQuery, ItemRead

router = APIRouter(prefix="/items", tags=["items"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=Page[ItemRead])
async def list_items(db: DbSession, q: Annotated[ItemQuery, Query()]):
    items, total = await item_repo.list_items(db, q)
    return Page(items=items, total=total, skip=q.skip, limit=q.limit)


@router.post("/search", response_model=Page[ItemRead])
async def search_items(db: DbSession, q: ItemQuery):
    """Same as GET /items but filters are sent as a JSON body."""
    items, total = await item_repo.list_items(db, q)
    return Page(items=items, total=total, skip=q.skip, limit=q.limit)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(db: DbSession, item_id: int):
    item = await item_repo.get(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(db: DbSession, data: ItemCreate):
    return await item_repo.create(db, data)
