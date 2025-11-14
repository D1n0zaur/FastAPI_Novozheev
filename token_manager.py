from typing import Optional, Dict
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel

class SessionInfo(BaseModel):
    username: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime

class TokenManager:
    def __init__(self):
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_timeout = timedelta(minutes=2)
    
    def create_session(self, username: str) -> str:
        session_token = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + self.session_timeout

        session_info = SessionInfo(
            username=username,
            created_at=now,
            expires_at=expires_at,
            last_activity=now
        )

        self.active_sessions[session_token] = session_info
        return session_token

    def verify_session(self, session_token: str) -> Optional[SessionInfo]:
        if session_token not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_token]
        now = datetime.now()
        
        if now > session.expires_at:
            self.delete_session(session_token)
            return None

        session.last_activity = now
        session.expires_at = now + self.session_timeout

        return session
    
    def delete_session(self, session_token: str) -> bool:
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False
    
    def get_user_sessions(self, username: str) -> Dict[str, SessionInfo]:
        return {
            token: session for token, session in self.active_sessions.items()
            if session.username == username
        }
    
    def cleanup_expired_sessions(self) -> int:
        now = datetime.now()
        expired_tokens = [
            token for token, session in self.active_sessions.items()
            if now > session.expires_at
        ]

        for token in expired_tokens:
            self.delete_session(token)

        return len(expired_tokens)
    
    def get_session_stats(self, session_token: str) -> Optional[dict]:
        session = self.verify_session(session_token)
        if not session:
            return None
        
        now = datetime.now()
        total_duration = now - session.created_at 
        idle_time = now - session.last_activity
        remaining_time = session.expires_at - now

        return {
            "session_age_seconds": total_duration.total_seconds(),
            "idle_time_seconds": idle_time.total_seconds(),
            "remaining_time_seconds": remaining_time.total_seconds(),
            "is_near_expiry": remaining_time < timedelta(minutes=1),
            "formatted_remaining": str(remaining_time).split('.')[0]
        }

token_manager = TokenManager()