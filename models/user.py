from sqlalchemy.orm import Mapped , mapped_column
from db.session import Base
# from models.base import UserRole
from datetime import datetime, timezone

class User(Base):
    
    __tablename__ = "users"

    user_id : Mapped[int] = mapped_column(primary_key=True , index=True)
    username : Mapped[str] = mapped_column(index=True ,unique=True , nullable=False)
    email : Mapped[str] = mapped_column(nullable=False , unique=True , index= True)
    hashed_password : Mapped[str] = mapped_column(nullable=False , index=True)

    is_active : Mapped[bool] = mapped_column(default=True ,nullable=False )
    is_verified : Mapped[bool] = mapped_column(default=False , nullable=False)

    # role : Mapped[UserRole] = mapped_column(default=UserRole.USER, nullable=False)

    created_at : Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc) , nullable=False)
    updated_at : Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc) , onupdate=datetime.now(timezone.utc), nullable=False)
    last_login : Mapped[datetime] = mapped_column(nullable=True)