"""Attachment upload and download endpoints."""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from server.api.dependencies import current_user
from server.services.attachment_service import AttachmentService
from server.services.message_service import MessageService
from server.repositories.chats import ChatRepository
from server.database import transaction

router=APIRouter(tags=["attachments"])
storage=AttachmentService(); service=MessageService(); chats=ChatRepository()

@router.post("/chats/{chat_id}/attachments")
async def direct_upload(chat_id:int,file:UploadFile=File(...),user=Depends(current_user)):
    if user["id"] not in chats.direct_members(chat_id): raise HTTPException(status_code=404,detail="Chat not found.")
    attachment=await storage.store(file)
    return service.send("direct",chat_id,user["id"],"",attachment)

@router.post("/groups/{group_id}/attachments")
async def group_upload(group_id:int,file:UploadFile=File(...),user=Depends(current_user)):
    if user["id"] not in chats.group_members(group_id): raise HTTPException(status_code=404,detail="Group not found.")
    attachment=await storage.store(file)
    return service.send("group",group_id,user["id"],"",attachment)

@router.get("/attachments/{chat_type}/{message_id}")
def download(chat_type:str,message_id:int,user=Depends(current_user)):
    if chat_type not in {"direct","group"}: raise HTTPException(status_code=400,detail="Invalid chat type.")
    table="messages" if chat_type=="direct" else "group_messages"
    parent="conversation_id" if chat_type=="direct" else "group_id"
    with transaction() as db:
        row=db.execute(f"""SELECT m.attachment_filename,m.attachment_disk_name,m.deleted_at
            FROM {table} m WHERE m.id=? AND EXISTS(
            SELECT 1 FROM {'conversations c' if chat_type=='direct' else 'group_members gm'}
            WHERE {'c.id=m.conversation_id AND (c.user1_id=? OR c.user2_id=?)' if chat_type=='direct' else 'gm.group_id=m.group_id AND gm.user_id=?'})""",
            (message_id,user["id"],user["id"]) if chat_type=="direct" else (message_id,user["id"])).fetchone()
    if not row or not row["attachment_disk_name"] or row["deleted_at"]:
        raise HTTPException(status_code=404,detail="Attachment not found.")
    path=storage.path_for(row["attachment_disk_name"])
    if not path.is_file(): raise HTTPException(status_code=404,detail="File missing.")
    return FileResponse(path,filename=row["attachment_filename"],media_type="application/octet-stream")
