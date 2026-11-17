"""Send, edit, delete, and search messages."""
from fastapi import APIRouter, Depends, HTTPException
from server.api.dependencies import current_user
from server.api.schemas import MessageCreate, MessageEdit
from server.services.message_service import MessageService
from server.database import transaction
from server.realtime import hub
from server.repositories.chats import ChatRepository
chat_repo=ChatRepository()
from shared.timeutils import utc_iso

router=APIRouter(tags=["messages"])
service=MessageService()

@router.post("/chats/{chat_id}/messages")
async def send_direct(chat_id:int,payload:MessageCreate,user=Depends(current_user)):
    try:
        message=service.send("direct",chat_id,user["id"],payload.body)
        await hub.send_many(chat_repo.direct_members(chat_id),{"type":"new_message","chat_type":"direct","chat_id":chat_id,"message":message})
        return message
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.post("/groups/{group_id}/messages")
async def send_group(group_id:int,payload:MessageCreate,user=Depends(current_user)):
    try:
        message=service.send("group",group_id,user["id"],payload.body)
        await hub.send_many(chat_repo.group_members(group_id),{"type":"new_message","chat_type":"group","chat_id":group_id,"message":message})
        return message
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.patch("/chats/{chat_id}/messages/{message_id}")
async def edit_direct(chat_id:int,message_id:int,payload:MessageEdit,user=Depends(current_user)):
    try:
        if user["id"] not in chat_repo.direct_members(chat_id): raise PermissionError("Not a member.")
        result=service.edit("direct",chat_id,message_id,user["id"],payload.body)
        await hub.send_many(chat_repo.direct_members(chat_id),{"type":"message_updated","chat_type":"direct","chat_id":chat_id,"message":result})
        return result
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.patch("/groups/{group_id}/messages/{message_id}")
async def edit_group(group_id:int,message_id:int,payload:MessageEdit,user=Depends(current_user)):
    try:
        if user["id"] not in chat_repo.group_members(group_id): raise PermissionError("Not a member.")
        result=service.edit("group",group_id,message_id,user["id"],payload.body)
        await hub.send_many(chat_repo.group_members(group_id),{"type":"message_updated","chat_type":"group","chat_id":group_id,"message":result})
        return result
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.delete("/chats/{chat_id}/messages/{message_id}")
async def delete_direct(chat_id:int,message_id:int,user=Depends(current_user)):
    try:
        if user["id"] not in chat_repo.direct_members(chat_id): raise PermissionError("Not a member.")
        result=service.delete("direct",chat_id,message_id,user["id"])
        await hub.send_many(chat_repo.direct_members(chat_id),{"type":"message_updated","chat_type":"direct","chat_id":chat_id,"message":result})
        return result
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.delete("/groups/{group_id}/messages/{message_id}")
async def delete_group(group_id:int,message_id:int,user=Depends(current_user)):
    try:
        if user["id"] not in chat_repo.group_members(group_id): raise PermissionError("Not a member.")
        result=service.delete("group",group_id,message_id,user["id"])
        await hub.send_many(chat_repo.group_members(group_id),{"type":"message_updated","chat_type":"group","chat_id":group_id,"message":result})
        return result
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.get("/messages/search")
def search_messages(q:str,user=Depends(current_user)):
    term=f"%{q.strip()}%"
    if not q.strip(): return []
    with transaction() as db:
        direct=db.execute("""SELECT m.id,m.conversation_id AS chat_id,'direct' AS chat_type,
            m.sender_id,u.username AS sender_username,m.body,m.created_at
            FROM messages m JOIN conversations c ON c.id=m.conversation_id JOIN users u ON u.id=m.sender_id
            WHERE (c.user1_id=? OR c.user2_id=?) AND m.body LIKE ? AND m.deleted_at IS NULL
            ORDER BY m.id DESC LIMIT 50""",(user["id"],user["id"],term)).fetchall()
        group=db.execute("""SELECT m.id,m.group_id AS chat_id,'group' AS chat_type,
            m.sender_id,u.username AS sender_username,m.body,m.created_at
            FROM group_messages m JOIN group_members gm ON gm.group_id=m.group_id
            JOIN users u ON u.id=m.sender_id WHERE gm.user_id=? AND m.body LIKE ?
            AND m.deleted_at IS NULL ORDER BY m.id DESC LIMIT 50""",(user["id"],term)).fetchall()
    return [dict(row) for row in list(direct)+list(group)]
