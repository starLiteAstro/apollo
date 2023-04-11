import enum

from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import discord_snowflake, int_pk, timestamp, user_id
from models.models import Base
from models.user import User


class VoteType(enum.Enum):
    basic = 0
    fptp = 1
    approval = 2
    stv = 3
    ranked_pairs = 4


class Vote(Base):
    __tablename__ = "vote"
    id: Mapped[int_pk]
    owner_id: Mapped[user_id]
    type: Mapped[VoteType]
    ranked_choice: Mapped[bool]
    created_at: Mapped[timestamp]
    title: Mapped[str] = mapped_column(default="Vote")
    vote_limit: Mapped[int] = mapped_column(default=0)
    seats: Mapped[int] = mapped_column(default=1)

    choices: Mapped[list["VoteChoice"]] = relationship(init=False)
    discord_vote: Mapped["DiscordVote"] = relationship(init=False)


class VoteChoice(Base):
    __tablename__ = "vote_choice"
    vote_id: Mapped[int] = mapped_column(
        ForeignKey("vote.id", ondelete="CASCADE"),
        primary_key=True
    )
    vote: Mapped[Vote] = relationship(init=False)
    choice_index: Mapped[int] = mapped_column(primary_key=True)
    choice: Mapped[str]

    user_votes: Mapped[list["UserVote"]] = relationship(
        cascade="all, delete-orphan", init=False
    )


class UserVote(Base):
    __tablename__ = "user_vote"
    vote_id: Mapped[int] = mapped_column(
        ForeignKey(Vote.id, ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True)
    user: Mapped[User] = relationship(init=False)
    choice: Mapped[int] = mapped_column(primary_key=True)
    vote_choice: Mapped[VoteChoice] = relationship(init=False)
    preference: Mapped[int] = mapped_column(default=0, init=False)
    ForeignKeyConstraint(
        (vote_id, choice),
        (VoteChoice.vote_id, VoteChoice.choice_index),
        ondelete="CASCADE",
    )


# Currently pretty useless
# TODO Limit to role
class DiscordVote(Base):
    __tablename__ = "discord_vote"
    id: Mapped[int] = mapped_column(
        ForeignKey(Vote.id, ondelete="CASCADE"),
        primary_key=True,
    )
    vote: Mapped["Vote"] = relationship(init=False)
    allowed_role_id: Mapped[int | None]

    messages: Mapped[list["DiscordVoteMessage"]] = relationship(init=False)


class DiscordVoteMessage(Base):
    __tablename__ = "discord_vote_message"
    message_id: Mapped[discord_snowflake] = mapped_column(primary_key=True)
    channel_id: Mapped[discord_snowflake]
    vote_id: Mapped[int] = mapped_column(
        ForeignKey("discord_vote.id", ondelete="CASCADE"),
        ForeignKey("vote.id", ondelete="CASCADE"),
    )
    choices_start_index: Mapped[int]
    numb_choices: Mapped[int] = mapped_column(default=20, init=False)
    part: Mapped[int]

    discord_vote: Mapped["DiscordVote"] = relationship(init=False)


# # TODO Add unique constraints, remove emoji
class DiscordVoteChoice(Base):
    __tablename__ = "discord_vote_choice"
    vote_id: Mapped[int] = mapped_column(primary_key=True)
    choice_index: Mapped[int] = mapped_column(primary_key=True)
    msg_id: Mapped[discord_snowflake | None] = mapped_column(
        ForeignKey(DiscordVoteMessage.message_id, ondelete="CASCADE")
    )
    msg: Mapped[DiscordVoteMessage] = relationship(init=False)
    emoji: Mapped[str | None] = mapped_column(default="", init=False)
    __table_args__ = (ForeignKeyConstraint(
        (vote_id, choice_index), (VoteChoice.vote_id, VoteChoice.choice_index)
    ),)
    choice: Mapped[VoteChoice] = relationship(init=False)
