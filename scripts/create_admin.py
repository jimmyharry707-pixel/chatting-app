"""Create a first admin user interactively for a private test deployment."""
import getpass
from server.database import initialize_database
from server.repositories.users import UserRepository
from server.security import hash_password
from shared.validators import validate_username,validate_password

def main():
    initialize_database()
    username=validate_username(input("Admin username: "))
    password=validate_password(getpass.getpass("Admin password: "))
    users=UserRepository()
    if users.by_username(username):
        raise SystemExit("That username already exists; no account was changed.")
    user_id=users.create(username,hash_password(password))
    print(f"Created account id={user_id}. Group admin roles are assigned per group.")
if __name__=="__main__": main()
