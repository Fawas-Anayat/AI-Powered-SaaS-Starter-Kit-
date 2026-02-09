from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func
from db.session import Base
from datetime import datetime


class User(Base):

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)  # ❌ no index

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    refresh_tokens = relationship(
        "Refresh_Token",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserSession(Base):

    __tablename__ = "user_sessions"  

    session_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    jti: Mapped[str] = mapped_column(index=True, nullable=False, unique=True)

    browser: Mapped[str] = mapped_column(index=True, nullable=True)
    ip_address: Mapped[str] = mapped_column(index=True, nullable=True)

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_revoked: Mapped[bool] = mapped_column(nullable=False, default=False)  

    user = relationship("User", back_populates="sessions")

    refresh_tokens = relationship(
        "Refresh_Token",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class Refresh_Token(Base):

    __tablename__ = "refresh_tokens"

    token_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("user_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
    session = relationship("UserSession", back_populates="refresh_tokens")
