# 프로필 관련 API 엔드포인트 (사용자 정보 조회)
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import date
from src.models.auth.user import User, Gender
from src.auth.dependencies import get_current_user, get_current_phone_number

router = APIRouter(prefix="/profile", tags=["프로필"])


# 사용자 프로필 응답 스키마 (앱으로 보내는 데이터 형식)
class UserProfileResponse(BaseModel):
    phone_number: str
    name: str
    given_name: str
    family_name: str
    gender: Gender
    birthdate: date
    phone_number_verified: bool
    
    class Config:
        from_attributes = True  # SQLAlchemy 모델을 Pydantic 모델로 변환 허용


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자의 프로필 조회
    - JWT 토큰으로 인증된 사용자 정보를 반환
    - get_current_user가 자동으로 토큰 검증 및 DB 조회 수행
    
    [앱의 요청 예시]
    GET /profile/me
    Authorization: Bearer <JWT_토큰>
    
    [응답 예시]
    {
      "phone_number": "+821012345678",
      "name": "홍길동",
      "given_name": "길동",
      "family_name": "홍",
      "gender": "남자",
      "birthdate": "1990-01-01",
      "phone_number_verified": true
    }
    """
    return current_user  # User 객체가 자동으로 UserProfileResponse로 변환됨


@router.get("/phone")
async def get_my_phone(
    phone_number: str = Depends(get_current_phone_number)
):
    """
    현재 로그인한 사용자의 전화번호만 조회
    - 전화번호만 필요한 경우 사용
    - 예: 주문 시 고객 전화번호 확인용
    """
    return {"phone_number": phone_number}

