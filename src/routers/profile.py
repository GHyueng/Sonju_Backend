# 프로필 관련 API 엔드포인트 (사용자 정보 조회)
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import date
from src.models.auth.user import User, Gender
from src.auth.dependencies import get_current_user, get_current_phone_number

router = APIRouter(prefix="/profile", tags=["프로필"])


# 사용자 프로필 응답 스키마
class UserProfileResponse(BaseModel):
    phone_number: str
    name: str
    gender: Gender
    birthdate: date
    
    class Config:
        from_attributes = True                                  # SQLAlchemy 모델을 Pydantic 모델로 변환 허용


#현재 로그인한 사용자의 프로필 조회
@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(                                       # JWT 토큰으로 인증된 사용자 정보를 반환
    current_user: User = Depends(get_current_user)              # get_current_user가 자동으로 토큰 검증 및 DB 조회 수행
):
    return current_user                                         # User 객체가 자동으로 UserProfileResponse로 변환됨


#현재 로그인한 사용자의 전화번호 조회
@router.get("/phone")
async def get_my_phone(
    phone_number: str = Depends(get_current_phone_number)):  
    return {"phone_number": phone_number}

