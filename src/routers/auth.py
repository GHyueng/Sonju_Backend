# 인증 관련 API 엔드포인트 (회원가입)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date
from src.db.database import get_db
from src.models.auth.user import User, Gender
from src.auth.dependencies import get_current_user, get_current_phone_number

router = APIRouter(prefix="/auth", tags=["인증"])


# 회원가입 요청 스키마 (앱에서 보내는 데이터 형식)
class SignUpRequest(BaseModel):
    phone_number: str = Field(..., description="전화번호 (예: +821012345678)")
    cognito_id: str = Field(..., description="Cognito에서 발급받은 고유 ID (sub)")
    given_name: str = Field(..., description="이름")
    family_name: str = Field(..., description="성")
    gender: Gender = Field(..., description="성별 (남자/여자)")
    birthdate: date = Field(..., description="생년월일 (YYYY-MM-DD)")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    db: Session = Depends(get_db)
):
    """
    회원가입 엔드포인트
    - 앱이 Cognito에 직접 가입 후 받은 정보를 백엔드 DB에 저장
    - Cognito 인증은 이미 완료된 상태 (앱이 처리)
    
    [앱의 회원가입 흐름]
    1. 앱 → Cognito: 전화번호/비밀번호로 회원가입
    2. Cognito → 앱: cognito_id (sub) 발급
    3. 앱 → 백엔드: 이 API를 호출하여 사용자 정보 저장
    """
    # 이미 존재하는 전화번호인지 확인
    existing_user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 전화번호입니다"
        )
    
    # 이미 존재하는 cognito_id인지 확인
    existing_cognito = db.query(User).filter(User.cognito_id == request.cognito_id).first()
    if existing_cognito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 Cognito ID입니다"
        )
    
    # 새 사용자 생성
    new_user = User(
        phone_number=request.phone_number,
        cognito_id=request.cognito_id,
        given_name=request.given_name,
        family_name=request.family_name,
        gender=request.gender,
        birthdate=request.birthdate,
        name=f"{request.family_name}{request.given_name}",  # 전체 이름 조합
        phone_number_verified=True  # Cognito를 통해 인증되었다고 가정
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "회원가입이 완료되었습니다",
        "phone_number": new_user.phone_number,
        "name": new_user.name
    }

