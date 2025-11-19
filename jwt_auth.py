from fastapi import HTTPException, Depends, Header
from typing import Optional
from jwt_manager import jwt_manager, TokenData

# Получение текущего пользователя из токена
async def get_current_user(authorization: Optional[str] = Header(None)) -> TokenData:
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Проверяем формат заголовка
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Извлекаем токен
    token = authorization.replace("Bearer ", "")
    
    # Верифицируем токен
    token_data = jwt_manager.verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token_data

async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[TokenData]:
    if authorization is None or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    return jwt_manager.verify_token(token)

valid_users = {
    "admin": {"password": "password123", "user_id": 1},
    "user": {"password": "123456", "user_id": 2},
    "demo": {"password": "demo", "user_id": 3}
}