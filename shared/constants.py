"""Shared protocol constants and application limits."""
APP_NAME = "Northstar Messenger"
APP_VERSION = "3.0.0"
API_PREFIX = "/api/v1"
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 32
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MAX_MESSAGE_LENGTH = 4000
MAX_GROUP_MEMBERS = 50
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200
SESSION_LIFETIME_DAYS = 30
EVENT_NEW_MESSAGE = "new_message"
EVENT_MESSAGE_UPDATED = "message_updated"
EVENT_TYPING = "typing"
EVENT_PRESENCE = "presence"
EVENT_READ_RECEIPT = "read_receipt"
EVENT_GROUP_ADDED = "group_added"
EVENT_GROUP_REMOVED = "group_removed"
ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".txt",
    ".csv", ".docx", ".xlsx", ".zip", ".mp3", ".wav", ".ogg"
}
