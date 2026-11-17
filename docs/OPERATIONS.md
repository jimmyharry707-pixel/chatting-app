# Operations

## Database
The default database is `server/chat.db`. Set `CHAT_DB_PATH` to change it. Use `scripts/backup_database.py backup-copy.db` to create a consistent SQLite backup.

## Uploads
The default attachment directory is `server/uploads`. Set `CHAT_UPLOAD_DIR` to move it. Back up the database and uploads together.

## Health
`GET /health` returns service status and version. Run `python -m scripts.health_check --url http://127.0.0.1:8000` from the project root.

## LAN test
Start the backend on a trusted LAN, allow TCP port 8000 in Windows Firewall, then enter the server private IP in the client login window. Do not forward this port from a home router to the public internet.
