from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EncryptedType  # type: ignore

from config import CONFIG
from models.karma import KarmaChange
from models.models import Base, discord_snowflake, timestamp


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_uid: Mapped[discord_snowflake]
    username: Mapped[str] = mapped_column(
        EncryptedType(type_in=String, key=CONFIG.BOT_SECRET_KEY)
    )
    karma_changes: Mapped[list["KarmaChange"]] = relationship(
        back_populates="user", order_by=KarmaChange.created_at, init=False
    )
    first_seen: Mapped[timestamp] = mapped_column(init=False)
    last_seen: Mapped[timestamp] = mapped_column(init=False)

    uni_id = mapped_column(
        EncryptedType(type_in=String, key=CONFIG.BOT_SECRET_KEY), nullable=True
    )
    verified_at = mapped_column(
        EncryptedType(type_in=DateTime, key=CONFIG.BOT_SECRET_KEY), nullable=True
    )
