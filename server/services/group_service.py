"""Group creation, membership, and role policy."""
from server.database import transaction
from shared.timeutils import utc_iso
from shared.constants import MAX_GROUP_MEMBERS
from shared.validators import validate_group_title
from shared.errors import PermissionDenied, ResourceNotFound, ValidationError

class GroupService:
    def create(self, owner_id, title, member_ids):
        title=validate_group_title(title)
        members=set(member_ids); members.discard(owner_id)
        if len(members)+1>MAX_GROUP_MEMBERS: raise ValidationError("Group member limit exceeded.")
        with transaction() as db:
            if members:
                marks=",".join("?" for _ in members)
                found=db.execute(f"SELECT id FROM users WHERE id IN ({marks})",tuple(members)).fetchall()
                if len(found)!=len(members): raise ResourceNotFound("One or more users do not exist.")
            cur=db.execute("INSERT INTO groups(title,owner_id,created_at) VALUES(?,?,?)",(title,owner_id,utc_iso()))
            group_id=cur.lastrowid
            all_ids=members|{owner_id}
            db.executemany("INSERT INTO group_members(group_id,user_id,role,joined_at) VALUES(?,?,?,?)",
                           [(group_id,i,"admin" if i==owner_id else "member",utc_iso()) for i in all_ids])
        return {"id":group_id,"chat_type":"group","title":title,"member_count":len(all_ids)}
    def members(self, group_id, requester_id):
        with transaction() as db:
            access=db.execute("SELECT role FROM group_members WHERE group_id=? AND user_id=?",(group_id,requester_id)).fetchone()
            if not access: raise ResourceNotFound("Group not found.")
            rows=db.execute("""SELECT u.id,u.username,u.display_name,u.bio,gm.role
                FROM group_members gm JOIN users u ON u.id=gm.user_id WHERE gm.group_id=? ORDER BY gm.role DESC,u.username""",(group_id,)).fetchall()
            return [dict(row) for row in rows]
    def add_members(self, group_id, actor_id, member_ids):
        with transaction() as db:
            role=db.execute("SELECT role FROM group_members WHERE group_id=? AND user_id=?",(group_id,actor_id)).fetchone()
            if not role: raise ResourceNotFound("Group not found.")
            if role["role"]!="admin": raise PermissionDenied("Only admins can add members.")
            existing={r["user_id"] for r in db.execute("SELECT user_id FROM group_members WHERE group_id=?",(group_id,))}
            new=set(member_ids)-existing
            if len(existing)+len(new)>MAX_GROUP_MEMBERS: raise ValidationError("Group member limit exceeded.")
            if new:
                marks=",".join("?" for _ in new)
                found=db.execute(f"SELECT id FROM users WHERE id IN ({marks})",tuple(new)).fetchall()
                if len(found)!=len(new): raise ResourceNotFound("User not found.")
                db.executemany("INSERT INTO group_members(group_id,user_id,role,joined_at) VALUES(?,?,'member',?)",
                               [(group_id,i,utc_iso()) for i in new])
        return {"status":"members_added","added":len(new)}
    def remove_member(self, group_id, actor_id, target_id):
        with transaction() as db:
            actor=db.execute("SELECT role FROM group_members WHERE group_id=? AND user_id=?",(group_id,actor_id)).fetchone()
            target=db.execute("SELECT role FROM group_members WHERE group_id=? AND user_id=?",(group_id,target_id)).fetchone()
            if not actor or not target: raise ResourceNotFound("Membership not found.")
            if actor_id!=target_id and actor["role"]!="admin": raise PermissionDenied("Only admins can remove others.")
            if target["role"]=="admin":
                count=db.execute("SELECT COUNT(*) AS n FROM group_members WHERE group_id=? AND role='admin'",(group_id,)).fetchone()["n"]
                if count<=1: raise ValidationError("Promote another admin before leaving.")
            db.execute("DELETE FROM group_members WHERE group_id=? AND user_id=?",(group_id,target_id))
        return {"status":"member_removed"}
