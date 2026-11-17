"""Authentication orchestration."""
from server.repositories.users import UserRepository
from server.security import hash_password, verify_password, issue_token, revoke_token
from shared.validators import validate_username, validate_password
from shared.errors import AuthenticationError, ConflictError

class AuthService:
    def __init__(self): self.users=UserRepository()
    def register(self, username, password):
        username=validate_username(username); validate_password(password)
        if self.users.by_username(username): raise ConflictError("Username is already taken.")
        user_id=self.users.create(username,hash_password(password))
        return {"access_token":issue_token(user_id),"user":self.users.by_id(user_id)}
    def login(self, username, password):
        user=self.users.by_username(username.strip())
        if not user or not verify_password(password,user["password_hash"]):
            raise AuthenticationError("Incorrect username or password.")
        return {"access_token":issue_token(user["id"]),"user":self.users.by_id(user["id"])}
    def logout(self, token): revoke_token(token)
