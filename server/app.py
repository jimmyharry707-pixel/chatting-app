"""FastAPI application composition root."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from server.database import initialize_database
from server.api import auth_routes,user_routes,chat_routes,message_routes,attachment_routes
from server.security import resolve_token
from server.realtime import hub
from server.config import settings

app=FastAPI(title="Northstar Messenger API",version="3.0.0",
            description="Modular real-time messaging backend for the PyQt5 desktop application.")
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),
                   allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(auth_routes.router,prefix="/api/v1")
app.include_router(user_routes.router,prefix="/api/v1")
app.include_router(chat_routes.router,prefix="/api/v1")
app.include_router(message_routes.router,prefix="/api/v1")
app.include_router(attachment_routes.router,prefix="/api/v1")

@app.on_event("startup")
def startup():
    settings.upload_dir.mkdir(parents=True,exist_ok=True)
    initialize_database()

@app.get("/health")
def health():
    return {"status":"ok","version":"3.0.0"}

@app.websocket("/ws")
async def websocket_endpoint(socket:WebSocket,token:str=Query(...)):
    user=resolve_token(token)
    if not user:
        await socket.close(code=4401)
        return
    await hub.websocket(socket,user)
