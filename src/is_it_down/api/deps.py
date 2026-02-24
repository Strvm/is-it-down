from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from is_it_down.db.session import get_db_session


async def db_session_dep() -> AsyncIterator[AsyncSession]:
    async for session in get_db_session():
        yield session
