from fastapi import HTTPException, Cookie, Depends
from typing import Optional
from token_manager import token_manager, SessionInfo

async def get_current_user(session_token: Optional[str] = Cookie(None)) -> SessionInfo:
    if not session_token:
        raise HTTPException(status_code=401, detail="Session not found")
    
    session = token_manager.verify_session(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Not active or old session")
    
    return session

async def get_optional_user(session_token: Optional[str] = Cookie(None)) -> Optional[SessionInfo]:
    if not session_token:
        return None
    
    return token_manager.verify_session(session_token)

valid_users = {
    "admin": "password123",
    "user": "123456",
    "demo": "demo"
}