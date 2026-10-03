from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemQuery


def _apply_filters(stmt: Select, q: ItemQuery) -> Select:
    if q.name:
        stmt = stmt.where(Item.name.ilike(f"%{q.name}%"))
    if q.min_price is not None:
        stmt = stmt.where(Item.price >= q.min_price)
    if q.max_price is not None:
        stmt = stmt.where(Item.price <= q.max_price)
    return stmt


async def list_items(db: AsyncSession, q: ItemQuery) -> tuple[list[Item], int]:
    stmt = _apply_filters(select(Item), q)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))

    sort_col = getattr(Item, q.sort_by)
    stmt = stmt.order_by(sort_col.desc() if q.sort_order == "desc" else sort_col.asc())
    result = await db.execute(stmt.offset(q.skip).limit(q.limit))
    return list(result.scalars().all()), total or 0


async def get(db: AsyncSession, item_id: int) -> Item | None:
    return await db.get(Item, item_id)


async def create(db: AsyncSession, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
