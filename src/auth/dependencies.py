from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.cognito_config import cognito_auth
from src.db.database import get_db
from src.models.auth.user import User

security = HTTPBearer()                 # FastAPI의 내장 HTTPBearer 보안 스키마를 사용해서 클라이언트 요청의 헤더에 포함된 토큰을 자동으로 추출

async def get_current_user_cognito_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    try:
        payload = cognito_auth.verify(token)
        cognito_id = payload.get("sub")
        if not cognito_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에 사용자 ID(sub)가 없습니다"
            )
        return cognito_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 검증 실패: {str(e)}"
        )

async def get_current_user(
    cognito_id: str = Depends(get_current_user_cognito_id),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.cognito_id == cognito_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    return user

async def get_current_phone_number(
    user: User = Depends(get_current_user)
) -> str:
    return user.phone_number
