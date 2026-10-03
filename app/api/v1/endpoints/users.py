from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbSession, get_current_superuser
from app.repositories import user_repo
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_superuser)])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(db: DbSession, data: UserCreate):
    if await user_repo.get_by_username(db, data.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    return await user_repo.create(db, data)
