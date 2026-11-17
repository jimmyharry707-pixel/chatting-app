# Northstar Messenger 3.0

A modular Windows desktop messaging application built with Python, PyQt5, FastAPI, SQLite, and WebSockets.

## Included structure

- `client/`: desktop application, reusable widgets, dialogs, REST client, WebSocket worker.
- `server/`: API composition, authentication, persistence repositories, domain services, attachment storage, realtime hub.
- `shared/`: shared validation, constants, timestamps, and errors.
- `tests/`: validation, security, presence, and timestamp tests.
- `scripts/`: database backup, health check, and admin account bootstrap helper.
- `docs/`: architecture, API, operations, and security notes.

## Features in this codebase

- Registration and login with PBKDF2 password hashes and opaque bearer tokens.
- Direct conversations and group creation/member administration.
- Message history, send, edit, delete, search, and attachment transfers.
- WebSocket event transport for live messages, presence, and typing signals.
- User display names and bios.
- SQLite foreign keys, indexes, transactions, and additive migrations.
- Windows batch scripts for installation, server startup, and client startup.

## Run on Windows

1. Install Python 3.10+.
2. Run `install_windows.bat`.
3. Run `run_server.bat` and leave it open.
4. Run `run_client.bat` in another terminal.
5. Register two accounts and test using two desktop client instances.

The default server address is `http://127.0.0.1:8000`. For LAN use, enter the server computer's private IP and allow TCP port 8000 in Windows Firewall.

## Tests

```bat
.venv\Scripts\python.exe -m pytest tests
```

## API documentation

With the backend running, open `http://127.0.0.1:8000/docs`.

## Prototype limitations

This is a development prototype, not a secure replacement for Telegram. It does not provide end-to-end encryption, voice/video calls, push notification infrastructure, Redis-backed multi-worker presence, rate limiting, antivirus scanning, encrypted backups, or account recovery. Use HTTPS/WSS behind a production reverse proxy before any internet deployment. Review the API permission paths and add integration tests before exposing it to users.
