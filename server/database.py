"""SQLite transactions, schema creation, and additive migrations."""
import sqlite3
from contextlib import contextmanager
from server.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT NOT NULL COLLATE NOCASE UNIQUE,password_hash TEXT NOT NULL,display_name TEXT NOT NULL DEFAULT '',bio TEXT NOT NULL DEFAULT '',avatar_path TEXT,created_at TEXT NOT NULL,last_seen TEXT);
CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,expires_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY,user1_id INTEGER NOT NULL REFERENCES users(id),user2_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,CHECK(user1_id<user2_id),UNIQUE(user1_id,user2_id));
CREATE TABLE IF NOT EXISTS groups(id INTEGER PRIMARY KEY,title TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',owner_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS group_members(group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,role TEXT NOT NULL DEFAULT 'member',joined_at TEXT NOT NULL,PRIMARY KEY(group_id,user_id));
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,sender_id INTEGER NOT NULL REFERENCES users(id),body TEXT NOT NULL DEFAULT '',attachment_filename TEXT,attachment_disk_name TEXT,attachment_size INTEGER,created_at TEXT NOT NULL,edited_at TEXT,deleted_at TEXT);
CREATE TABLE IF NOT EXISTS group_messages(id INTEGER PRIMARY KEY,group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,sender_id INTEGER NOT NULL REFERENCES users(id),body TEXT NOT NULL DEFAULT '',attachment_filename TEXT,attachment_disk_name TEXT,attachment_size INTEGER,created_at TEXT NOT NULL,edited_at TEXT,deleted_at TEXT);
CREATE TABLE IF NOT EXISTS conversation_reads(conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,last_read_message_id INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(conversation_id,user_id));
CREATE TABLE IF NOT EXISTS group_reads(group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,last_read_message_id INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(group_id,user_id));
CREATE TABLE IF NOT EXISTS message_reactions(id INTEGER PRIMARY KEY,message_id INTEGER NOT NULL,chat_type TEXT NOT NULL,user_id INTEGER NOT NULL REFERENCES users(id),emoji TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(message_id,chat_type,user_id,emoji));
CREATE TABLE IF NOT EXISTS contacts(owner_id INTEGER NOT NULL REFERENCES users(id),contact_id INTEGER NOT NULL REFERENCES users(id),nickname TEXT,created_at TEXT NOT NULL,PRIMARY KEY(owner_id,contact_id));
CREATE TABLE IF NOT EXISTS blocked_users(owner_id INTEGER NOT NULL REFERENCES users(id),blocked_id INTEGER NOT NULL REFERENCES users(id),created_at TEXT NOT NULL,PRIMARY KEY(owner_id,blocked_id));
CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(conversation_id,id);
CREATE INDEX IF NOT EXISTS idx_group_messages_chat ON group_messages(group_id,id);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
"""

def connect():
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.database_path), timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=20000")
    return conn

@contextmanager
def transaction():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    with transaction() as conn:
        conn.executescript(SCHEMA)
        additions = {
            "users": {"display_name":"TEXT NOT NULL DEFAULT ''","bio":"TEXT NOT NULL DEFAULT ''","avatar_path":"TEXT","last_seen":"TEXT"},
            "messages": {"attachment_filename":"TEXT","attachment_disk_name":"TEXT","attachment_size":"INTEGER","edited_at":"TEXT","deleted_at":"TEXT"},
            "group_messages": {"attachment_filename":"TEXT","attachment_disk_name":"TEXT","attachment_size":"INTEGER","edited_at":"TEXT","deleted_at":"TEXT"},
        }
        for table, columns in additions.items():
            existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
            for name, definition in columns.items():
                if name not in existing:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
