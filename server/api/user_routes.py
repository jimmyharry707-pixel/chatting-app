"""User search and profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from server.api.dependencies import current_user
from server.api.schemas import ProfilePatch
from server.repositories.users import UserRepository

router=APIRouter(tags=["users"])
repo=UserRepository()

@router.get("/users")
def search_users(search:str=Query(default="",max_length=64),user=Depends(current_user)):
    if not search.strip(): return []
    rows=repo.search(user["id"],search)
    return [{**row,"is_online":False} for row in rows]

@router.patch("/me")
def update_profile(payload:ProfilePatch,user=Depends(current_user)):
    display=(payload.display_name if payload.display_name is not None else user.get("display_name") or user["username"]).strip()
    bio=(payload.bio if payload.bio is not None else user.get("bio") or "").strip()
    if not display: display=user["username"]
    if len(bio)>160: raise HTTPException(status_code=400,detail="Bio too long.")
    return repo.update_profile(user["id"],display,bio)
