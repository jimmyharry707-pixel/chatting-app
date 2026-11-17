"""Safe local attachment storage."""
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from server.config import settings
from shared.constants import ALLOWED_ATTACHMENT_EXTENSIONS

class AttachmentService:
    async def store(self, upload: UploadFile):
        filename=Path((upload.filename or "attachment").replace("\\","/")).name
        suffix=Path(filename).suffix.lower()
        if suffix not in ALLOWED_ATTACHMENT_EXTENSIONS:
            raise HTTPException(status_code=400,detail="Unsupported file type.")
        data=await upload.read(settings.max_upload_bytes+1)
        if not data: raise HTTPException(status_code=400,detail="File is empty.")
        if len(data)>settings.max_upload_bytes: raise HTTPException(status_code=413,detail="File exceeds upload limit.")
        settings.upload_dir.mkdir(parents=True,exist_ok=True)
        disk_name=f"{uuid.uuid4().hex}{suffix}"
        (settings.upload_dir/disk_name).write_bytes(data)
        return {"filename":filename,"disk_name":disk_name,"size":len(data)}
    def path_for(self,disk_name):
        candidate=(settings.upload_dir/disk_name).resolve()
        if candidate.parent!=settings.upload_dir.resolve(): raise HTTPException(status_code=400,detail="Invalid file path.")
        return candidate
