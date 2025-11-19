import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel

class TokenData(BaseModel):
    username: str
    user_id: Optional[int] = None
    exp: datetime

class JWTManager:
    def __init__(self):
        self.secret_key = "ya-pridumal-jwt-key-sam-cifri-dlya-bezopasnosti-1835650937-wo-kak"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def create_access_token(self, username: str, user_id: Optional[int] = None) -> str:
        # Полезная нагрузка токена
        payload = {
            "sub": username,        # стандартное поле
            "username": username,   # имя пользователя
            "user_id": user_id,     # ID пользователя
            "iat": datetime.now(timezone.utc),  # Время создания токена
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)  # Время истечения токена
        }
        
        # Создание JWT токена
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        try:
            # Декодирование и проверка токена
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Извлекаем данные
            username = payload.get("username")
            user_id = payload.get("user_id")
            exp_timestamp = payload.get("exp")
            
            if not username or not exp_timestamp:
                return None
            
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            
            return TokenData(
                username=username,
                user_id=user_id,
                exp=exp_datetime
            )
            
        except jwt.ExpiredSignatureError:
            # Токен истек
            return None
        except jwt.InvalidTokenError:
            # Невалидный токен
            return None
        except Exception:
            # Любая другая ошибка
            return None
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            return None
        except:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        expiry = self.get_token_expiry(token)
        if not expiry:
            return True
        
        # Сравниваем с текущим временем
        return datetime.now(timezone.utc) > expiry

jwt_manager = JWTManager()