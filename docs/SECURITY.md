# Security checklist

- Passwords are hashed with PBKDF2-HMAC-SHA256 and per-user random salts.
- Session tokens are random opaque values; only SHA-256 token digests are stored.
- SQLite foreign keys are enabled on each connection.
- User text is HTML-escaped before message rendering.
- Upload extensions are allowlisted, names are normalized, and server storage names are random.
- Attachment download checks that the authenticated user belongs to the target conversation.
- Group membership and sender ownership are checked in service/repository paths.

Before production:
- Deploy only behind HTTPS/WSS and a hardened reverse proxy.
- Add request rate limits, login throttling, abuse reporting, and account recovery.
- Scan uploaded files and consider object storage with private signed downloads.
- Add CSRF/origin policy if cookie auth is introduced.
- Add secrets management, audit logs, backups, retention policy, and incident response.
- Conduct a security review; this prototype is not end-to-end encrypted.
