"""Registration, login, logout, and current-account endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException
from server.api.dependencies import current_user
from server.api.schemas import Credentials
from server.services.auth import AuthService
from server.security import revoke_token
from shared.errors import MessengerError

router=APIRouter(prefix="/auth",tags=["authentication"])
service=AuthService()

@router.post("/register")
def register(payload:Credentials):
    try: return service.register(payload.username,payload.password)
    except MessengerError as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.post("/login")
def login(payload:Credentials):
    try: return service.login(payload.username,payload.password)
    except MessengerError as exc: raise HTTPException(status_code=401,detail=str(exc))

@router.post("/logout")
def logout(user=Depends(current_user),authorization:str=Header(default="")):
    revoke_token(authorization.split(" ",1)[1])
    return {"status":"logged_out"}

@router.get("/me")
def me(user=Depends(current_user)):
    return {k:v for k,v in user.items() if k!="expires_at"}
