"""Direct-chat and group membership queries."""
from server.database import transaction
from shared.timeutils import utc_iso

class ChatRepository:
    def open_direct(self, first_id, second_id):
        if first_id==second_id: raise ValueError("Cannot message yourself.")
        left,right=sorted((first_id,second_id))
        with transaction() as db:
            row=db.execute("SELECT id FROM conversations WHERE user1_id=? AND user2_id=?",(left,right)).fetchone()
            if row: chat_id=row["id"]
            else:
                cur=db.execute("INSERT INTO conversations(user1_id,user2_id,created_at) VALUES(?,?,?)",(left,right,utc_iso()))
                chat_id=cur.lastrowid
            return {"id":int(chat_id),"chat_type":"direct"}
    def direct_members(self, chat_id):
        with transaction() as db:
            row=db.execute("SELECT user1_id,user2_id FROM conversations WHERE id=?",(chat_id,)).fetchone()
            return {int(row[0]),int(row[1])} if row else set()
    def group_members(self, group_id):
        with transaction() as db:
            rows=db.execute("SELECT user_id FROM group_members WHERE group_id=?",(group_id,)).fetchall()
            return {int(row[0]) for row in rows}
    def list_for_user(self, user_id):
        with transaction() as db:
            direct=db.execute("""SELECT c.id,peer.id AS peer_id,peer.username,peer.display_name,
                (SELECT body FROM messages WHERE conversation_id=c.id ORDER BY id DESC LIMIT 1) AS preview,
                (SELECT created_at FROM messages WHERE conversation_id=c.id ORDER BY id DESC LIMIT 1) AS latest
                FROM conversations c JOIN users peer ON peer.id=CASE WHEN c.user1_id=? THEN c.user2_id ELSE c.user1_id END
                WHERE c.user1_id=? OR c.user2_id=?""",(user_id,user_id,user_id)).fetchall()
            groups=db.execute("""SELECT g.id,g.title,
                (SELECT body FROM group_messages WHERE group_id=g.id ORDER BY id DESC LIMIT 1) AS preview,
                (SELECT created_at FROM group_messages WHERE group_id=g.id ORDER BY id DESC LIMIT 1) AS latest
                FROM groups g JOIN group_members gm ON gm.group_id=g.id WHERE gm.user_id=?""",(user_id,)).fetchall()
            result=[]
            for row in direct:
                result.append({"id":row["id"],"chat_type":"direct","title":row["display_name"] or row["username"],
                               "peer":{"id":row["peer_id"],"username":row["username"]},
                               "last_message":row["preview"],"last_message_at":row["latest"]})
            for row in groups:
                result.append({"id":row["id"],"chat_type":"group","title":row["title"],
                               "last_message":row["preview"],"last_message_at":row["latest"]})
            return sorted(result,key=lambda item:item["last_message_at"] or "",reverse=True)
