# JWT 토큰 검증 및 사용자 정보 조회 의존성
from fastapi import Depends, HTTPException, status      

# 클라이언트의 요청 헤더(Authorization)에서 Bearer 토큰을 추출하기 위한 모듈
# - HTTPBearer: 'Authorization: Bearer <token>' 형식의 헤더를 파싱
# - HTTPAuthorizationCredentials: 추출된 토큰 정보를 담는 객체
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

# AWS Cognito 설정과 인증 객체(cognito_auth)를 불러옴
# - cognito_auth.verify(token)으로 JWT 토큰의 유효성 검증 수행
from src.auth.cognito_config import cognito_auth

# 데이터베이스 연결 세션을 FastAPI의 Depends()로 주입하기 위한 함수
# - get_db()는 요청마다 새로운 DB 세션을 열고, 요청이 끝나면 자동으로 닫음
from src.db.database import get_db

# User 테이블 모델 정의를 import
# - cognito_id, phone_number 등 사용자 정보를 ORM으로 접근하기 위해 사용
from src.models.auth.user import User

# Bearer 토큰 추출을 위한 스키마 (모바일 앱의 Authorization 헤더에서 토큰 추출)
security = HTTPBearer()


async def get_current_user_cognito_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    1단계: Authorization 헤더에서 JWT 토큰을 받아 Cognito 검증
    - 모바일 앱이 보낸 Bearer 토큰을 추출
    - fastapi-cognito를 사용해 토큰의 서명, 만료시간, 발급자 검증
    - 검증 성공 시 cognito_id (sub 클레임) 반환
    
    [앱의 요청 예시]
    GET /api/profile/me
    Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    token = credentials.credentials  # "Bearer <토큰>"에서 토큰 부분만 추출
    
    try:
        # Cognito의 공개키(JWKS)로 토큰 검증 및 페이로드 추출
        payload = cognito_auth.verify(token)
        
        # 'sub' 클레임이 Cognito에서 발급하는 고유 사용자 ID
        cognito_id = payload.get("sub")
        
        if not cognito_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에 사용자 ID(sub)가 없습니다"
            )
        
        return cognito_id  # 예: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        
    except Exception as e:
        # 토큰이 유효하지 않거나 만료된 경우
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 검증 실패: {str(e)}"
        )


async def get_current_user(
    cognito_id: str = Depends(get_current_user_cognito_id),
    db: Session = Depends(get_db)
) -> User:
    """
    2단계: cognito_id로 데이터베이스에서 사용자 정보 조회
    - 1단계에서 검증된 cognito_id를 받음
    - DB의 users 테이블에서 해당 cognito_id를 가진 사용자 조회
    - 사용자 객체(User) 반환 - 이 객체에 전화번호 등 모든 정보 포함
    
    [데이터 흐름]
    JWT 토큰 → cognito_id 추출 → DB 조회 → User 객체 반환
    """
    user = db.query(User).filter(User.cognito_id == cognito_id).first()
    
    if not user:
        # cognito_id는 유효하지만 DB에 사용자 정보가 없는 경우
        # (Cognito에는 가입했지만 백엔드 DB에는 등록 안 된 경우)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user  # User 객체 반환 (phone_number, name, gender 등 모든 정보 포함)


async def get_current_phone_number(
    user: User = Depends(get_current_user)
) -> str:
    """
    3단계: 전화번호만 필요한 경우 사용하는 편의 함수
    - 2단계에서 조회한 User 객체에서 전화번호만 추출하여 반환
    - 전화번호 기반 비즈니스 로직에 활용
    """
    return user.phone_number
