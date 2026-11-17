"""Pydantic request and response contracts."""
from pydantic import BaseModel, Field
from typing import Optional

class Credentials(BaseModel):
    username: str
    password: str
class ProfilePatch(BaseModel):
    display_name: Optional[str]=Field(default=None,max_length=48)
    bio: Optional[str]=Field(default=None,max_length=160)
class GroupCreate(BaseModel):
    title: str=Field(min_length=2,max_length=64)
    member_ids: list[int]=Field(default_factory=list)
class MemberList(BaseModel):
    member_ids: list[int]=Field(min_length=1,max_length=50)
class MessageCreate(BaseModel):
    body: str=Field(default="",max_length=4000)
class MessageEdit(BaseModel):
    body: str=Field(min_length=1,max_length=4000)
class ReactionCreate(BaseModel):
    emoji: str=Field(min_length=1,max_length=16)
