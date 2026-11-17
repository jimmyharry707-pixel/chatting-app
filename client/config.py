"""Desktop client settings."""
import os
from dataclasses import dataclass

@dataclass
class ClientSettings:
    server_url:str=os.getenv("CHAT_SERVER_URL","http://127.0.0.1:8000")
    reconnect_seconds:int=3
    request_timeout:int=15
    max_message_preview:int=72
    window_width:int=1280
    window_height:int=820

settings=ClientSettings()
