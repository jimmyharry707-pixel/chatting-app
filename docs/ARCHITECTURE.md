# Architecture

The desktop UI is deliberately separate from backend persistence. PyQt widgets emit user intent; `client.api.APIClient` maps that intent to HTTP calls; `client.realtime.RealtimeWorker` receives server events on a worker thread and emits Qt signals.

The FastAPI composition root in `server.app` registers route modules. Route modules validate request shape and call domain services. Services enforce business rules and coordinate repositories. Repositories contain SQL and return dictionaries so the service layer does not expose sqlite row objects.

`shared` contains contracts that do not depend on either FastAPI or PyQt. This keeps username and message rules consistent.

## Request path

1. A user action occurs in a Qt widget.
2. The main window calls the API client.
3. The API client sends an authenticated request.
4. FastAPI resolves the bearer token.
5. The route delegates to a service.
6. The service validates membership and operation rules.
7. A repository performs a transaction.
8. The route returns JSON.

## Realtime path

The WebSocket endpoint authenticates the session token. `RealtimeHub` tracks active sockets in process memory and forwards typing/presence events. A production multi-worker deployment should replace the in-memory hub with Redis pub/sub and shared presence keys.
