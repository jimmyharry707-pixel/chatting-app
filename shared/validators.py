"""Input validation independent of the UI and web framework."""
import re
from pathlib import Path
from shared.constants import *
from shared.errors import ValidationError

def validate_username(value: str) -> str:
    value = (value or "").strip()
    if not MIN_USERNAME_LENGTH <= len(value) <= MAX_USERNAME_LENGTH:
        raise ValidationError("Username must be 3-32 characters.")
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ValidationError("Use letters, numbers, and underscores only.")
    return value

def validate_password(value: str) -> str:
    if not MIN_PASSWORD_LENGTH <= len(value or "") <= MAX_PASSWORD_LENGTH:
        raise ValidationError("Password must be 8-128 characters.")
    return value

def validate_message(value: str) -> str:
    value = (value or "").strip()
    if not value or len(value) > MAX_MESSAGE_LENGTH:
        raise ValidationError("Message must contain 1-4000 characters.")
    return value

def validate_group_title(value: str) -> str:
    value = (value or "").strip()
    if not 2 <= len(value) <= 64:
        raise ValidationError("Group title must contain 2-64 characters.")
    return value

def validate_attachment_name(value: str) -> str:
    name = Path((value or "attachment").replace("\\", "/")).name
    if Path(name).suffix.lower() not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError("Unsupported file extension.")
    return name
