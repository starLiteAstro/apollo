import logging
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, MetaData, create_engine, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session, mapped_column
from typing_extensions import Annotated

from config import CONFIG

# this is bad, redo this
engine = create_engine(CONFIG.DATABASE_CONNECTION, future=True)

from config import CONFIG

engine = create_engine(CONFIG.DATABASE_CONNECTION)
if CONFIG.SQL_LOGGING:
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
db_session = Session(bind=engine, future=True)

# some useful re-usable column types
int_pk = Annotated[int, mapped_column(primary_key=True, init=False)]
user_id = Annotated[int, mapped_column(ForeignKey("users.id"))]
# discord 'snowflakes' are the really long IDs that you get as like channel or user IDs
# this annotated column map type uses BigInteger to encode those and convert to python ints
discord_snowflake = Annotated[int, mapped_column(BigInteger)]
timestamp = Annotated[
    datetime,
    mapped_column(
        default_factory=datetime.now, insert_default=func.current_timestamp()
    ),
]


class Base(MappedAsDataclass, DeclarativeBase):
    """
    Base model for all of Apollo's Models
    Uses SQLAlchemy's declarative dataclass mapping API
    """

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
