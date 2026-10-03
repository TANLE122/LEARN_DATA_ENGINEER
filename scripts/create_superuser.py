"""Create the auth table (if missing) and a superuser.

Usage:
    python -m scripts.create_superuser <username>
"""

import argparse
import asyncio
import getpass

from app.db.session import AsyncSessionLocal, engine
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import UserCreate


async def main(username: str, password: str) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: User.__table__.create(c, checkfirst=True))

    async with AsyncSessionLocal() as db:
        if await user_repo.get_by_username(db, username):
            print(f"User '{username}' already exists")
            return
        await user_repo.create(db, UserCreate(username=username, password=password, is_superuser=True))
        print(f"Superuser '{username}' created")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    args = parser.parse_args()
    pwd = getpass.getpass("Password: ")
    if pwd != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")
    asyncio.run(main(args.username, pwd))
