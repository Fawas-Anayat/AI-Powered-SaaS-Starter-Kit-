# from datetime import datetime, timedelta
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship , Mapped , mapped_column 
# from db.session import Base
# # from models.user import User

# class UserSession(Base):

#     __tablename__ = "User_sessions"

#     session_id : Mapped[int] = mapped_column(primary_key=True , index=True)
#     user_id : Mapped[int] = mapped_column(ForeignKey("users.user_id" , ondelete="CASCADE") , nullable=False , index=True)

#     jti : Mapped[str] = mapped_column(index=True , nullable=False , unique=True)

#     browser : Mapped[str] = mapped_column(index=True , nullable=True)
#     ip_address : Mapped[str] = mapped_column(index=True , nullable= True)

#     is_active : Mapped[bool] = mapped_column(nullable=False, default=True)
#     is_revoked : Mapped[bool] = mapped_column(default=True)


# class Refresh_Token(Base):

#     __tablename__ = "refresh_tokens"

#     token_id : Mapped[int] = mapped_column(primary_key=True , index=True)
#     user_id : Mapped[int] = mapped_column(ForeignKey("users.user_id") , onupdate="CASCADE" , index=True)
#     session_id : Mapped[int] = mapped_column(ForeignKey("User_sessions.session_id") , onupdate="CASCADE" , index=True)

#     is_active : Mapped[bool] = mapped_column(default=True , nullable=True)
#     is_revoked : Mapped[bool] = mapped_column(default=False , nullable=True)

#     user = relationship("User" , back_populates="refresh_tokens")