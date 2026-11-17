"""Message CRUD and read marker persistence."""
from server.database import transaction
from shared.timeutils import utc_iso

TABLES={"direct":("messages","conversation_id"),"group":("group_messages","group_id")}

class MessageRepository:
    def create(self, chat_type, chat_id, sender_id, body, attachment=None):
        table,parent=TABLES[chat_type]; attachment=attachment or {}
        with transaction() as db:
            cur=db.execute(f"""INSERT INTO {table}({parent},sender_id,body,created_at,
                attachment_filename,attachment_disk_name,attachment_size) VALUES(?,?,?,?,?,?,?)""",
                (chat_id,sender_id,body,utc_iso(),attachment.get("filename"),attachment.get("disk_name"),attachment.get("size")))
            message_id = int(cur.lastrowid)
        return self.get(chat_type, message_id)
    def get(self, chat_type, message_id):
        table,_=TABLES[chat_type]
        with transaction() as db:
            row=db.execute(f"""SELECT m.*,u.username AS sender_username,
                COALESCE(NULLIF(u.display_name,''),u.username) AS sender_display_name
                FROM {table} m JOIN users u ON u.id=m.sender_id WHERE m.id=?""",(message_id,)).fetchone()
            if not row: raise LookupError("Message not found.")
            return dict(row)
    def list(self, chat_type, chat_id, limit=100, before_id=None):
        table,parent=TABLES[chat_type]
        clause="AND m.id<?" if before_id else ""
        params=(chat_id,before_id,limit) if before_id else (chat_id,limit)
        with transaction() as db:
            rows=db.execute(f"""SELECT m.*,u.username AS sender_username,
                COALESCE(NULLIF(u.display_name,''),u.username) AS sender_display_name
                FROM {table} m JOIN users u ON u.id=m.sender_id
                WHERE m.{parent}=? {clause} ORDER BY m.id DESC LIMIT ?""",params).fetchall()
            return [dict(row) for row in reversed(rows)]
    def edit(self, chat_type, chat_id, message_id, sender_id, body):
        table,parent=TABLES[chat_type]
        with transaction() as db:
            row=db.execute(f"SELECT sender_id,deleted_at FROM {table} WHERE id=? AND {parent}=?",(message_id,chat_id)).fetchone()
            if not row: raise LookupError("Message not found.")
            if row["sender_id"]!=sender_id: raise PermissionError("Only the sender can edit this message.")
            if row["deleted_at"]: raise ValueError("Deleted message cannot be edited.")
            db.execute(f"UPDATE {table} SET body=?,edited_at=? WHERE id=?",(body,utc_iso(),message_id))
        return self.get(chat_type,message_id)
    def soft_delete(self, chat_type, chat_id, message_id, actor_id, admin=False):
        table,parent=TABLES[chat_type]
        with transaction() as db:
            row=db.execute(f"SELECT sender_id FROM {table} WHERE id=? AND {parent}=?",(message_id,chat_id)).fetchone()
            if not row: raise LookupError("Message not found.")
            if row["sender_id"]!=actor_id and not admin: raise PermissionError("Cannot delete this message.")
            db.execute(f"UPDATE {table} SET body='',attachment_filename=NULL,attachment_disk_name=NULL,attachment_size=NULL,deleted_at=? WHERE id=?",
                       (utc_iso(),message_id))
        return self.get(chat_type,message_id)
    def mark_read(self, chat_type, chat_id, user_id):
        read_table,parent=("conversation_reads","conversation_id") if chat_type=="direct" else ("group_reads","group_id")
        message_table,message_parent=TABLES[chat_type]
        with transaction() as db:
            latest=db.execute(f"SELECT COALESCE(MAX(id),0) AS n FROM {message_table} WHERE {message_parent}=?",(chat_id,)).fetchone()["n"]
            db.execute(f"""INSERT INTO {read_table}({parent},user_id,last_read_message_id) VALUES(?,?,?)
                ON CONFLICT({parent},user_id) DO UPDATE SET last_read_message_id=MAX(last_read_message_id,excluded.last_read_message_id)""",
                (chat_id,user_id,latest))
            return int(latest)
