from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

# Used to keep response time constant when the username does not exist
_DUMMY_HASH = hash_password("dummy-password")


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_by_username(db, username)
    if user is None:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        is_superuser=data.is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
