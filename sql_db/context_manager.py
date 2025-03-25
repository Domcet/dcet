from contextlib import asynccontextmanager
from asyncpg import UniqueViolationError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, delete
from sql_db.config import DB_URL
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound, IntegrityError


class AsyncDatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(DB_URL, echo=False)
        self.Session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create(self, model_class, **fields):
        """Asynchronously create a new record in the database."""
        async with self.Session() as session:
            async with session.begin():
                instance = model_class(**fields)
                session.add(instance)
                try:
                    await session.commit()
                except IntegrityError as ex:
                    # Check if the underlying cause of the IntegrityError is a UniqueViolationError
                    if isinstance(ex.orig.__cause__, UniqueViolationError):
                        # Do nothing or handle the duplicate case as needed
                        pass
                    else:
                        # Re-raise the exception if it's not a UniqueViolationError
                        raise
            return instance

    async def update(self, model_class, filter_by, **fields):
        """Asynchronously update an existing record in the database."""
        async with self.Session() as session:
            async with session.begin():
                stmt = update(model_class).where(filter_by).values(**fields)
                result = await session.execute(stmt)

                if result.rowcount == 0:
                    # Raise an exception if no rows were updated
                    raise NoResultFound(f"No {model_class.__name__} record found with the given criteria.")

            await session.commit()

    async def delete(self, model_class, filter_by):
        """Asynchronously delete a record from the database."""
        async with self.Session() as session:
            async with session.begin():
                stmt = delete(model_class).where(filter_by)
                await session.execute(stmt)
            await session.commit()

    async def fetch_one(self, model_class, filter_by):
        """Asynchronously fetch a single record from the database."""
        async with self.Session() as session:
            stmt = select(model_class).where(filter_by)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def fetch_all(self, model_class, filter_by):
        async with self.Session() as session:
            stmt = select(model_class).where(filter_by)
            result = await session.execute(stmt)
            return result.scalars().all()

    @asynccontextmanager
    async def transaction(self):
        """Asynchronous transaction context manager."""
        async with self.Session() as session:
            async with session.begin():
                try:
                    yield session  # Возвращает сессию в блок контекста
                    await session.commit()  # Завершение транзакции
                except Exception:
                    await session.rollback()  # Откат при ошибке
                    raise  # Повторно выбрасывает исключение
