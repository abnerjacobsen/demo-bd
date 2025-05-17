"""Custom SQLAlchemy type for identity columns: uses BigInteger, with fallback to Integer for SQLite.

This module defines a BigIntIdentity type for use in database models, ensuring compatibility across different database backends.
"""

from __future__ import annotations

from sqlalchemy.types import BigInteger, Integer

BigIntIdentity = BigInteger().with_variant(Integer, "sqlite")
# """A ``BigInteger`` variant that reverts to an ``Integer`` for unsupported variants."""
