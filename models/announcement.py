from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.models import Base, int_pk, timestamp, user_id
from models.user import User


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int_pk] = mapped_column(init=False)
    user_id: Mapped[user_id]
    announcement_content: Mapped[str]
    trigger_at: Mapped[datetime]
    triggered: Mapped[bool]
    playback_channel_id: Mapped[int]
    created_at: Mapped[timestamp]
    user: Mapped["User"] = relationship(
        "User",
        uselist=False,
    )
    irc_name: Mapped[str | None] = mapped_column(default=None)
