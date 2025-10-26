# 인증 관련 API 엔드포인트 (회원가입)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date
from src.db.database import get_db
from src.models.auth.user import User, Gender
from src.auth.dependencies import get_current_user, get_current_phone_number

router = APIRouter(prefix="/auth", tags=["인증"])


# 회원가입 요청 스키마
class SignUpRequest(BaseModel):
    phone_number: str = Field(...)
    cognito_id: str = Field(...)
    given_name: str = Field(...)
    family_name: str = Field(...)
    gender: Gender = Field(...)
    birthdate: date = Field(...)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,                                    # 클라이언트가 보낸 JSON 데이터를 SignUpRequest 객체로 자동 변환.
    db: Session = Depends(get_db)                              # 데이터베이스 연결 세션을 FastAPI의 의존성 주입(Dependency Injection) 으로 받아옴
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
    existing_user = (
        db.query(User)                                         # SQLAlchemy ORM을 이용해 users 테이블을 조회
        .filter(User.phone_number == request.phone_number)     # 전달받은 request.phone_number 값과 같은 전화번호가 이미 있는지 검사.
        .first()                                               # 첫 번째 결과를 반환 (없으면 None)                               
    )
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
        gender=request.gender,
        birthdate=request.birthdate,
        name=f"{request.family_name}{request.given_name}",  
    
    )
    
    db.add(new_user)                                     # 새 User 객체를 세션에 추가 준비
    db.commit()                                          # 변경사항을 데이터베이스에 커밋하여 실제로 저장
    db.refresh(new_user)                                 # 새로 생성된 사용자의 최신 상태를 가져옴
    
    return {
        "message": "회원가입이 완료되었습니다",
        "phone_number": new_user.phone_number,
        "name": new_user.name
    }

