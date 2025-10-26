from sqlalchemy import String, Boolean, Date, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
import enum
from src.db.database import Base


class Gender(str, enum.Enum):
    male = "남자"
    female = "여자"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("cognito_id", name="uq_users_cognito_id"),                                 # Cognito ID는 고유해야 함
    )

    phone_number: Mapped[str] = mapped_column(String(32), primary_key=True)                         # 전화번호가 각 유저를 고유하게 구분
    cognito_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)    # Cognito에서 발급하는 고유 ID(UUID)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)                            # 성별
    birthdate: Mapped[Date] = mapped_column(Date, nullable=False)                                   # 생년월일
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)                      # 전체 이름 (성 + 이름)
