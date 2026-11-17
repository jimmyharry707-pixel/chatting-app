# API contracts

All authenticated REST requests use `Authorization: Bearer <token>`.
The API returns JSON error objects with a `detail` field for expected failures.

## Authentication
- `POST /api/v1/auth/register`: `{username, password}`.
- `POST /api/v1/auth/login`: `{username, password}`.
- `POST /api/v1/auth/logout`: revoke the current token.
- `GET /api/v1/auth/me`: return the current account.

## Profiles and discovery
- `PATCH /api/v1/me`: optional `display_name` and `bio`.
- `GET /api/v1/users?search=term`: username/display-name search.

## Conversations
- `GET /api/v1/chats`: list direct and group conversations.
- `POST /api/v1/chats/{user_id}`: open a direct conversation.
- `POST /api/v1/groups`: create a group with `title` and `member_ids`.
- `GET /api/v1/groups/{group_id}/members`: list members.
- `POST /api/v1/groups/{group_id}/members`: add members (admin only).
- `DELETE /api/v1/groups/{group_id}/members/{member_id}`: leave/remove member.

## Messages
- `GET /api/v1/chats/{chat_id}/messages`: direct history.
- `GET /api/v1/groups/{group_id}/messages`: group history.
- `POST /api/v1/chats/{chat_id}/messages`: direct message `{body}`.
- `POST /api/v1/groups/{group_id}/messages`: group message `{body}`.
- `PATCH` and `DELETE` message resources for edit and soft-delete.
- `GET /api/v1/messages/search?q=term`: search accessible text history.

## Attachments
Multipart upload routes accept a single `file` part. The download route is
`GET /api/v1/attachments/{chat_type}/{message_id}`. Current upload limits and
extensions are defined in `shared.constants` and `server.config`.

## Realtime events
The WebSocket endpoint is `/ws?token=<session-token>`. Client events currently
include `typing`. Server events include `new_message`, `message_updated`,
`presence`, and group membership notifications.
