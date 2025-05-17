"""Database field types for encrypted strings.

Provides SQLAlchemy-compatible types and encryption backends for storing
encrypted string and text values in the database, supporting both Fernet
and PostgreSQL pgcrypto backends.
"""

from __future__ import annotations

import abc
import base64
import contextlib
import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy import func as sql_func

cryptography = None
with contextlib.suppress(ImportError):
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes

if TYPE_CHECKING:
    from sqlalchemy.engine import Dialect


class EncryptionBackend(abc.ABC):
    """Abstract base class for encryption backends.

    Defines the interface for mounting a vault, initializing the engine,
    and encrypting/decrypting values for use with SQLAlchemy types.
    """

    def mount_vault(self, key: str | bytes) -> None:
        """Mount the encryption vault with the provided key.

        Args:
            key (str | bytes): The encryption key to use for mounting the vault.
        """
        if isinstance(key, str):
            key = key.encode()

    @abc.abstractmethod
    def init_engine(self, key: bytes | str) -> None:  # pragma: nocover
        """Initialize the encryption engine with the provided key.

        Args:
            key (bytes | str): The encryption key to initialize the engine.
        """

    @abc.abstractmethod
    def encrypt(self, value: Any) -> str:  # pragma: nocover
        """Encrypt the given value and return the encrypted string.

        Args:
            value (Any): The value to encrypt.

        Returns
        -------
            str: The encrypted value as a string.
        """

    @abc.abstractmethod
    def decrypt(self, value: Any) -> str:  # pragma: nocover
        """Decrypt the given value and return the decrypted string.

        Args:
            value (Any): The value to decrypt.

        Returns
        -------
            str: The decrypted value as a string.
        """


class PGCryptoBackend(EncryptionBackend):
    """PG Crypto backend."""

    def init_engine(self, key: bytes | str) -> None:
        """Initialize the encryption engine with the provided key.

        Args:
            key (bytes | str): The encryption key to initialize the engine.
        """
        if isinstance(key, str):
            key = key.encode()
        self.passphrase = base64.urlsafe_b64encode(key)

    def encrypt(self, value: Any) -> str:
        """Encrypt the given value and return the encrypted string.

        Args:
            value (Any): The value to encrypt.

        Returns
        -------
            str: The encrypted value as a string.
        """
        if not isinstance(value, str):  # pragma: nocover
            value = repr(value)
        value = value.encode()
        return sql_func.pgp_sym_encrypt(value, self.passphrase)  # type: ignore[return-value]

    def decrypt(self, value: Any) -> str:
        """Decrypt the given value and return the decrypted string.

        Args:
            value (Any): The value to decrypt.

        Returns
        -------
            str: The decrypted value as a string.
        """
        if not isinstance(value, str):  # pragma: nocover
            value = str(value)
        return sql_func.pgp_sym_decrypt(value, self.passphrase)  # type: ignore[return-value]


class FernetBackend(EncryptionBackend):
    """Encryption Using a Fernet backend."""

    def mount_vault(self, key: str | bytes) -> None:
        """Mount the encryption vault with the provided key.

        Args:
            key (str | bytes): The encryption key to use for mounting the vault.
        """
        if isinstance(key, str):
            key = key.encode()
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())  # pyright: ignore[reportPossiblyUnboundVariable]
        digest.update(key)
        engine_key = digest.finalize()
        self.init_engine(engine_key)

    def init_engine(self, key: bytes | str) -> None:
        """Initialize the Fernet encryption engine with the provided key.

        Args:
            key (bytes | str): The encryption key to initialize the Fernet engine.
        """
        if isinstance(key, str):
            key = key.encode()
        self.key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(self.key)  # pyright: ignore[reportPossiblyUnboundVariable]

    def encrypt(self, value: Any) -> str:
        """Encrypt the given value and return the encrypted string.

        Args:
            value (Any): The value to encrypt.

        Returns
        -------
            str: The encrypted value as a string.
        """
        if not isinstance(value, str):
            value = repr(value)
        value = value.encode()
        encrypted = self.fernet.encrypt(value)
        return encrypted.decode("utf-8")

    def decrypt(self, value: Any) -> str:
        """Decrypt the given value and return the decrypted string.

        Args:
            value (Any): The value to decrypt.

        Returns
        -------
            str: The decrypted value as a string.
        """
        if not isinstance(value, str):  # pragma: nocover
            value = str(value)
        decrypted: str | bytes = self.fernet.decrypt(value.encode())
        if not isinstance(decrypted, str):
            decrypted = decrypted.decode("utf-8")
        return decrypted


class EncryptedString(TypeDecorator[str]):
    """Used to store encrypted values in a database."""

    impl = String
    cache_ok = True

    def __init__(
        self,
        key: str | bytes | Callable[[], str | bytes] | None = None,
        backend: type[EncryptionBackend] = FernetBackend,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        if key is None:
            key = os.urandom(32)
        self.key = key
        self.backend = backend()

    @property
    def python_type(self) -> type[str]:
        """Return the Python type handled by this custom type.

        Returns
        -------
            type[str]: The Python type (str) handled by this type.
        """
        return str

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        """Return the appropriate SQLAlchemy type for the given dialect.

        Args:
            dialect (Dialect): The SQLAlchemy dialect in use.

        Returns
        -------
            Any: The SQLAlchemy type descriptor appropriate for the dialect.
        """
        if dialect.name in {"mysql", "mariadb"}:
            return dialect.type_descriptor(Text())
        if dialect.name == "oracle":
            return dialect.type_descriptor(String(length=4000))
        return dialect.type_descriptor(String())

    def process_bind_param(self, value: Any, dialect: Dialect) -> str | None:
        """Encrypt the value before storing it in the database.

        Args:
            value (Any): The value to be encrypted and stored.
            dialect (Dialect): The SQLAlchemy dialect in use.

        Returns
        -------
            str | None: The encrypted value as a string, or None if value is None.
        """
        if value is None:
            return value
        self.mount_vault()
        return self.backend.encrypt(value)

    def process_result_value(self, value: Any, dialect: Dialect) -> str | None:
        """Decrypt the value after retrieving it from the database.

        Args:
            value (Any): The value to be decrypted after retrieval.
            dialect (Dialect): The SQLAlchemy dialect in use.

        Returns
        -------
            str | None: The decrypted value as a string, or None if value is None.
        """
        if value is None:
            return value
        self.mount_vault()
        return self.backend.decrypt(value)

    def mount_vault(self) -> None:
        """Mount the encryption vault using the configured key.

        This method resolves the encryption key, calling it if it is a callable,
        and mounts the vault in the backend with the resolved key.
        """
        key = self.key() if callable(self.key) else self.key
        self.backend.mount_vault(key)


class EncryptedText(EncryptedString):
    """Encrypted text (CLOB) type for storing encrypted large text values in the database."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        """Return the appropriate SQLAlchemy type for the given dialect.

        Args:
            dialect (Dialect): The SQLAlchemy dialect in use.

        Returns
        -------
            Any: The SQLAlchemy type descriptor appropriate for the dialect.
        """
        return dialect.type_descriptor(Text())
