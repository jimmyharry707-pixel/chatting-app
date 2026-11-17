"""Direct and group chat endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from server.api.dependencies import current_user
from server.api.schemas import GroupCreate, MemberList
from server.repositories.chats import ChatRepository
from server.services.group_service import GroupService
from server.services.message_service import MessageService

router=APIRouter(tags=["chats"])
chats=ChatRepository(); groups=GroupService(); messages=MessageService()

@router.get("/chats")
def list_chats(user=Depends(current_user)):
    return chats.list_for_user(user["id"])

@router.post("/chats/{other_user_id}")
def open_direct(other_user_id:int,user=Depends(current_user)):
    try: return chats.open_direct(user["id"],other_user_id)
    except ValueError as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.post("/groups")
def create_group(payload:GroupCreate,user=Depends(current_user)):
    try: return groups.create(user["id"],payload.title,payload.member_ids)
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.get("/groups/{group_id}/members")
def group_members(group_id:int,user=Depends(current_user)):
    try: return groups.members(group_id,user["id"])
    except Exception as exc: raise HTTPException(status_code=404,detail=str(exc))

@router.post("/groups/{group_id}/members")
def add_members(group_id:int,payload:MemberList,user=Depends(current_user)):
    try: return groups.add_members(group_id,user["id"],payload.member_ids)
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.delete("/groups/{group_id}/members/{member_id}")
def remove_member(group_id:int,member_id:int,user=Depends(current_user)):
    try: return groups.remove_member(group_id,user["id"],member_id)
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.get("/chats/{chat_id}/messages")
def direct_history(chat_id:int,user=Depends(current_user)):
    try: return messages.history("direct",chat_id,user["id"])
    except Exception as exc: raise HTTPException(status_code=404,detail=str(exc))

@router.get("/groups/{group_id}/messages")
def group_history(group_id:int,user=Depends(current_user)):
    try: return messages.history("group",group_id,user["id"])
    except Exception as exc: raise HTTPException(status_code=404,detail=str(exc))
