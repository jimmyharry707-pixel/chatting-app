"""User persistence queries."""
from server.database import transaction
from shared.timeutils import utc_iso

class UserRepository:
    def create(self, username, password_hash):
        with transaction() as db:
            cur=db.execute("INSERT INTO users(username,password_hash,display_name,created_at) VALUES(?,?,?,?)",
                           (username,password_hash,username,utc_iso()))
            return int(cur.lastrowid)
    def by_username(self, username):
        with transaction() as db:
            row=db.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE",(username,)).fetchone()
            return dict(row) if row else None
    def by_id(self, user_id):
        with transaction() as db:
            row=db.execute("SELECT id,username,display_name,bio,avatar_path,last_seen,created_at FROM users WHERE id=?",(user_id,)).fetchone()
            return dict(row) if row else None
    def update_profile(self, user_id, display_name, bio):
        with transaction() as db:
            db.execute("UPDATE users SET display_name=?,bio=? WHERE id=?",(display_name,bio,user_id))
            return dict(db.execute("SELECT id,username,display_name,bio,last_seen FROM users WHERE id=?",(user_id,)).fetchone())
    def search(self, current_user_id, query, limit=50):
        term=f"%{query.strip()}%"
        with transaction() as db:
            rows=db.execute("""SELECT id,username,display_name,bio,last_seen FROM users
                               WHERE id!=? AND (username LIKE ? COLLATE NOCASE OR display_name LIKE ? COLLATE NOCASE)
                               ORDER BY username LIMIT ?""",(current_user_id,term,term,limit)).fetchall()
            return [dict(row) for row in rows]
    def set_last_seen(self, user_id, value):
        with transaction() as db: db.execute("UPDATE users SET last_seen=? WHERE id=?",(value,user_id))
