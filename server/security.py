"""Password hashing and opaque session tokens."""
import base64, hashlib, hmac, secrets
from datetime import datetime, timedelta, timezone
from server.database import transaction
from server.config import settings

ITERATIONS = 310_000

def hash_password(password):
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

def verify_password(password, stored):
    try:
        algorithm, rounds, salt, digest=stored.split("$",3)
        if algorithm!="pbkdf2_sha256": return False
        actual=hashlib.pbkdf2_hmac("sha256",password.encode(),base64.b64decode(salt),int(rounds))
        return hmac.compare_digest(actual,base64.b64decode(digest))
    except (ValueError,TypeError): return False

def issue_token(user_id):
    token=secrets.token_urlsafe(40)
    digest=hashlib.sha256(token.encode()).hexdigest()
    expires=(datetime.now(timezone.utc)+timedelta(days=settings.token_days)).isoformat()
    with transaction() as db:
        db.execute("INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)",(digest,user_id,expires))
    return token

def resolve_token(token):
    digest=hashlib.sha256(token.encode()).hexdigest()
    with transaction() as db:
        row=db.execute("""SELECT u.id,u.username,u.display_name,u.bio,u.last_seen,s.expires_at
                          FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=?""",(digest,)).fetchone()
        if not row: return None
        try: expired=datetime.fromisoformat(row["expires_at"])<=datetime.now(timezone.utc)
        except ValueError: expired=True
        if expired:
            db.execute("DELETE FROM sessions WHERE token_hash=?",(digest,))
            return None
        return dict(row)

def revoke_token(token):
    digest=hashlib.sha256(token.encode()).hexdigest()
    with transaction() as db: db.execute("DELETE FROM sessions WHERE token_hash=?",(digest,))
