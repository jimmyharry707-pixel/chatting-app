"""Typed REST API client used by the desktop UI."""
from pathlib import Path
from urllib.parse import quote,urlparse
import requests
from shared.errors import NetworkError,AuthenticationError,MessengerError

class APIClient:
    def __init__(self,base_url):
        self.base_url=base_url.strip().rstrip("/")
        self.token=None
        if not self.base_url.startswith(("http://","https://")):
            raise ValueError("Server URL must use http:// or https://.")
    def headers(self):
        return {"Authorization":f"Bearer {self.token}"} if self.token else {}
    def request(self,method,path,**kwargs):
        headers=kwargs.pop("headers",{}); headers.update(self.headers())
        try:
            response=requests.request(method,self.base_url+path,headers=headers,timeout=20,**kwargs)
        except requests.RequestException as exc: raise NetworkError(str(exc)) from exc
        try: data=response.json() if response.content else {}
        except ValueError: data={}
        if not response.ok:
            message=str(data.get("detail",f"HTTP {response.status_code}"))
            if response.status_code==401: raise AuthenticationError(message)
            raise MessengerError(message)
        return data
    def register(self,username,password):
        data=self.request("POST","/api/v1/auth/register",json={"username":username,"password":password})
        self.token=data["access_token"]; return data
    def login(self,username,password):
        data=self.request("POST","/api/v1/auth/login",json={"username":username,"password":password})
        self.token=data["access_token"]; return data
    def logout(self):
        if self.token:
            try: self.request("POST","/api/v1/auth/logout")
            finally: self.token=None
    def me(self): return self.request("GET","/api/v1/auth/me")
    def update_profile(self,name,bio): return self.request("PATCH","/api/v1/me",json={"display_name":name,"bio":bio})
    def search_users(self,q): return self.request("GET","/api/v1/users",params={"search":q})
    def chats(self): return self.request("GET","/api/v1/chats")
    def open_direct(self,user_id): return self.request("POST",f"/api/v1/chats/{user_id}")
    def create_group(self,title,member_ids): return self.request("POST","/api/v1/groups",json={"title":title,"member_ids":member_ids})
    def group_members(self,group_id): return self.request("GET",f"/api/v1/groups/{group_id}/members")
    def add_members(self,group_id,ids): return self.request("POST",f"/api/v1/groups/{group_id}/members",json={"member_ids":ids})
    def messages(self,kind,chat_id):
        route="groups" if kind=="group" else "chats"
        return self.request("GET",f"/api/v1/{route}/{chat_id}/messages")
    def send(self,kind,chat_id,body):
        route="groups" if kind=="group" else "chats"
        return self.request("POST",f"/api/v1/{route}/{chat_id}/messages",json={"body":body})
    def edit(self,kind,chat_id,message_id,body):
        route="groups" if kind=="group" else "chats"
        return self.request("PATCH",f"/api/v1/{route}/{chat_id}/messages/{message_id}",json={"body":body})
    def delete(self,kind,chat_id,message_id):
        route="groups" if kind=="group" else "chats"
        return self.request("DELETE",f"/api/v1/{route}/{chat_id}/messages/{message_id}")
    def search_messages(self,q): return self.request("GET","/api/v1/messages/search",params={"q":q})
    def upload(self,kind,chat_id,path):
        route="groups" if kind=="group" else "chats"
        with open(path,"rb") as handle:
            return self.request("POST",f"/api/v1/{route}/{chat_id}/attachments",
                files={"file":(Path(path).name,handle)},timeout=60)
    def download(self,kind,message_id,destination):
        response=requests.get(self.base_url+f"/api/v1/attachments/{kind}/{message_id}",
                              headers=self.headers(),timeout=60)
        if not response.ok: raise MessengerError("Attachment download failed.")
        Path(destination).write_bytes(response.content); return destination
    def websocket_url(self):
        parsed=urlparse(self.base_url); scheme="wss" if parsed.scheme=="https" else "ws"
        return f"{scheme}://{parsed.netloc}/ws?token={quote(self.token or '')}"
