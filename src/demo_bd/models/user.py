"""User model and repository definitions for the demo_bd application."""

from typing import Any

from sqlalchemy import String, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_bind_manager._repository import SQLAlchemyAsyncRepository
from sqlalchemy_json import mutable_json_type

from demo_bd.core.db.base import SlugKey, UUIDv7AuditBase
from demo_bd.core.db.manager import sa_manager

bind = sa_manager.get_bind()


class UserModel(bind.declarative_base, UUIDv7AuditBase, SlugKey):  # type: ignore
    """Represents a user in the system."""

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    mobile_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    data: Mapped[dict[str, Any]] = mapped_column(
        mutable_json_type(dbtype=JSONB, nested=True),
        nullable=False,
        default={},
        server_default=text("'{}'::jsonb"),
    )


__tablename__ = "users"
__mapper_args__ = {"eager_defaults": True}
__admin_icon__ = "fa-solid fa-comments"
__admin_label__ = "Users"
__admin_name__ = "User"
__admin_identity__ = "user"


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    """Repository for performing async operations on UserModel."""

    _model = UserModel

    # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#updating-using-the-excluded-insert-values
    async def upsert(
        self,
        name: str,
        mobile_number: str,
        data: dict | None = None,
    ) -> UserModel:
        """
        Insert a new user or update an existing user with the given mobile_number.

        If a user with the specified mobile_number already exists, update their name and updated_at fields.
        Otherwise, insert a new user with the provided name, whatsapmobile_numberp_uuid, and data.

        Args:
            name (str): The name of the user.
            mobile_number (str): The mobile number of the user.
            data (dict, optional): Additional user data. Defaults to {}.

        Returns
        -------
            UserModel: The inserted or updated user model instance.
        """
        if data is None:
            data = {}

        insert_stmt = insert(self._model).values(
            name=name,
            whatsapp_uuid=mobile_number,
            data=data,
        )
        stmt = insert_stmt.on_conflict_do_update(
            index_elements=[
                self._model.mobile_number,
            ],
            set_={
                "name": name,
                "updated_at": insert_stmt.excluded.updated_at,
            },
        ).returning(self._model)

        async with self._get_session() as session:
            result = await session.execute(stmt)
            return result.scalars().one()

    async def find_by_mobile_number(
        self,
        mobile_number: str,
    ) -> UserModel | None:
        """
        Retrieve a user by their mobile number.

        Args:
            mobile_number (str): The mobile number to search for.

        Returns
        -------
            UserModel | None: The user model instance if found, otherwise None.
        """
        # stmt = select(self._model).where(
        #     and_(
        #         self._model.mobile_number == mobile_number,
        #     )
        # )
        stmt = select(self._model).where(
            self._model.mobile_number == mobile_number,
        )

        async with self._get_session() as session:
            result = await session.execute(stmt)
            return result.scalars().one_or_none()


def get_memory_repo(sa_manager) -> UserRepository:
    """
    Create a UserRepository instance using the provided SQLAlchemy manager.

    Args:
        sa_manager: The SQLAlchemy manager to get the bind from.

    Returns
    -------
        UserRepository: An instance of UserRepository bound to the given manager.
    """
    return UserRepository(sa_manager.get_bind())
