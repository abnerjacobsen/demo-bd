import typing as t

from sqlalchemy import Column, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from demo_bd.core.db.manager import sa_manager

bind = sa_manager.get_bind()

T = t.TypeVar("T", bound="AbstractModel")


class AbstractModel(bind.declarative_base):  # type: ignore
    """Base class for all models."""

    __abstract__ = True
    __allow_unmapped__ = True

    def to_dict(self) -> dict:
        """Convert the data to a dictionary."""
        return {
            f"{self.__tablename__}_{col.name}": getattr(self, col.name)
            for col in t.cast(list[Column], self.__table__.columns)
        }

    @staticmethod
    def _get_column(
        model: type[T],
        col: InstrumentedAttribute[t.Any],
    ) -> str:
        """Get the name of a column in a model."""
        name = col.name
        if name not in model.__table__.columns:
            raise ValueError(f"Column {name} not found in {model.__name__}")
        return name

    @classmethod
    def _get_primary_key(cls) -> str:
        """Return the primary key of the model."""
        return cls.__table__.primary_key.columns[0].name

    @classmethod
    async def create(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        **kwargs,
    ) -> T:
        """Create a new record in the database."""
        async with sessionmaker() as async_session:
            instance = cls(**kwargs)
            async_session.add(instance)
            await async_session.commit()
            await async_session.refresh(instance)
            return instance

    @classmethod
    async def get(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        primary_key: int,
    ) -> T:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as async_session:
            return await async_session.get(cls, primary_key)

    @classmethod
    async def get_with_join(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        primary_key: int,
        join_tables: t.Any | list[t.Any] = None,
    ) -> T:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as async_session:
            statement = select(cls).filter_by(**{cls._get_primary_key(): primary_key})
            if join_tables is not None:
                statement = statement.options(selectinload(*join_tables))
            result = await async_session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def get_by_key(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        key: InstrumentedAttribute[t.Any],
        value: t.Any,
    ) -> T | None:
        """Get a record by a key."""
        async with sessionmaker() as async_session:
            statement = select(cls).filter_by(**{cls._get_column(cls, key): value})
            result = await async_session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def get_by_filter(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        **kwargs,
    ) -> T | None:
        """Get a record from the database by a filter."""
        async with sessionmaker() as async_session:
            statement = select(cls).filter_by(**kwargs)
            result = await async_session.execute(statement)
            return result.scalars().first()

    @classmethod
    async def update(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        primary_key: t.Any,
        **kwargs,
    ) -> T | None:
        """Update a record in the database."""
        async with sessionmaker() as session:
            instance = await session.get(cls, primary_key)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                return instance
            return None

    @classmethod
    async def update_by_key(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        key: InstrumentedAttribute[t.Any],
        value: t.Any,
        **kwargs,
    ) -> T | None:
        """Update a record in the database by a key."""
        async with sessionmaker() as async_session:
            instance = await cls.get_by_key(sessionmaker, key, value)
            if instance:
                for attr, new_value in kwargs.items():
                    setattr(instance, attr, new_value)
                async_session.add(instance)
                await async_session.commit()
            return instance

    @classmethod
    async def delete(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        primary_key: int,
    ) -> T | None:
        """Delete a record from the database by its primary key."""
        async with sessionmaker() as async_session:
            instance = await cls.get(sessionmaker, primary_key)
            if instance:
                await async_session.delete(instance)
                await async_session.commit()
            return instance

    @classmethod
    async def delete_by_key(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        key: InstrumentedAttribute[t.Any],
        value: t.Any,
    ) -> T | None:
        """Delete a record from the database by a key."""
        async with sessionmaker() as async_session:
            instance = await cls.get_by_key(sessionmaker, key, value)
            if instance:
                await async_session.delete(instance)
                await async_session.commit()
            return instance

    @classmethod
    async def delete_by_filter(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        **kwargs,
    ) -> T | None:
        """Delete a record from the database by a filter."""
        async with sessionmaker() as async_session:
            instance = await cls.get_by_filter(sessionmaker, **kwargs)
            if instance:
                await async_session.delete(instance)
                await async_session.commit()
            return instance

    @classmethod
    async def create_or_update(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        **kwargs,
    ) -> T:
        """Get and update a record from the database by its primary key."""
        primary_key = kwargs.get(cls._get_primary_key())
        instance = await cls.get(sessionmaker, primary_key) if primary_key else None
        if instance:
            await cls.update(sessionmaker, primary_key, **kwargs)
            return instance
        return await cls.create(sessionmaker, **kwargs)

    @classmethod
    async def exists(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        primary_key: int,
    ) -> bool:
        """Check if a record exists in the database by its primary key."""
        async with sessionmaker() as async_session:
            return await async_session.get(cls, primary_key) is not None

    @classmethod
    async def exists_by_filter(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        **kwargs,
    ) -> bool:
        """Check if a record exists in the database by a filter."""
        async with sessionmaker() as async_session:
            statement = select(cls).filter_by(**kwargs).order_by(cls.id.asc())
            result = await async_session.execute(statement)
            return bool(result.scalar())

    @classmethod
    async def paginate(  # noqa: PLR0913
        cls: type[T],
        sessionmaker: async_sessionmaker,
        page_number: int,
        page_size: int = 7,
        join_tables: t.Any | list[t.Any] = None,
        filters: t.Sequence[t.Any] | None = None,
        order_by: Column | None = None,
    ) -> t.Sequence[T]:
        """Get paginated records from the database by a filter."""
        async with sessionmaker() as async_session:
            statement = select(cls).limit(page_size).offset((page_number - 1) * page_size)
            if filters is not None:
                statement = statement.filter(*filters)
            if join_tables is not None:
                statement = statement.join(*join_tables).options(selectinload(*join_tables))
            if order_by is not None:
                statement = statement.order_by(order_by)
            result = await async_session.execute(statement)
            return result.scalars().all()

    @classmethod
    async def total_pages(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        page_size: int = 7,
        join_tables: t.Any | list[t.Any] = None,
        filters: t.Sequence[t.Any] | None = None,
    ) -> int:
        async with sessionmaker() as async_session:
            statement = select(func.count(cls.__table__.primary_key.columns[0]))
            if filters is not None:
                statement = statement.filter(*filters)
            if join_tables is not None:
                statement = statement.join(*join_tables)
            query = await async_session.execute(statement)
            return (query.scalar() + page_size - 1) // page_size

    @classmethod
    async def all(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        join_tables: t.Any | list[t.Any] = None,
    ) -> t.Sequence[T]:
        """Get all records from the database."""
        async with sessionmaker() as async_session:
            statement = select(cls)
            if join_tables is not None:
                statement = statement.options(selectinload(*join_tables))
            result = await async_session.execute(statement)
            return result.scalars().all()

    @classmethod
    async def all_by_filter(
        cls: type[T],
        sessionmaker: async_sessionmaker,
        join_tables: t.Any | list[t.Any] = None,
        **kwargs,
    ) -> t.Sequence[T]:
        """Get all records from the database by a filter."""
        async with sessionmaker() as async_session:
            statement = select(cls).filter_by(**kwargs)
            if join_tables is not None:
                statement = statement.options(selectinload(*join_tables))
            result = await async_session.execute(statement)
            return result.scalars().all()
