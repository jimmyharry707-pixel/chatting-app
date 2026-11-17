"""FastAPI authentication dependencies."""
from typing import Optional
from fastapi import Header, HTTPException
from server.security import resolve_token

def current_user(authorization: Optional[str]=Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401,detail="Authentication required.")
    user=resolve_token(authorization.split(" ",1)[1].strip())
    if not user: raise HTTPException(status_code=401,detail="Session expired.")
    return user
