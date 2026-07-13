# API Documentation

## Base URL

`http://localhost:8000/api/v1`

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header.

```bash
Authorization: Bearer <access_token>
```

Tokens are obtained from `POST /auth/login` or `POST /auth/register`. Access tokens expire after a configurable period (default 60 minutes). Refresh tokens are rotated on `POST /auth/refresh`.

## Endpoints

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | Public | Register a new user |
| POST | `/auth/login` | Public | Authenticate and receive tokens |
| POST | `/auth/refresh` | Public | Rotate refresh token |
| POST | `/auth/logout` | Public | Revoke refresh token |
| POST | `/auth/verify-email` | Public | Verify email with token |
| POST | `/auth/request-password-reset` | Public | Request password reset |
| POST | `/auth/reset-password` | Public | Reset password with token |

#### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"User"}'
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

#### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### User Management

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/users/me` | Yes | Get current user |
| PATCH | `/users/me` | Yes | Update current user |
| DELETE | `/users/me` | Yes | Soft-delete current user |

### Birth Profiles

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/profiles` | Yes | Create a birth profile |
| GET | `/profiles` | Yes | List user profiles |
| GET | `/profiles/{id}` | Yes | Get a profile |
| PATCH | `/profiles/{id}` | Yes | Update a profile |
| DELETE | `/profiles/{id}` | Yes | Soft-delete a profile |

### Conversations

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/conversations` | Yes | Create a conversation |
| GET | `/conversations` | Yes | List conversations |
| GET | `/conversations/{id}` | Yes | Get conversation details |
| POST | `/conversations/{id}/messages` | Yes | Add a message |
| POST | `/conversations/{id}/archive` | Yes | Archive conversation |
| POST | `/conversations/{id}/resume` | Yes | Resume archived conversation |
| DELETE | `/conversations/{id}` | Yes | Soft-delete conversation |
| GET | `/conversations/{id}/export` | Yes | Export conversation |

### Preferences

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/preferences` | Yes | Get preferences |
| PATCH | `/preferences` | Yes | Update preferences |

### Feedback

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/feedback` | Yes | Submit feedback |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"rating":"Helpful","comment":"Clear explanation"}'
```

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Service health check |

## Error Codes

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Unauthorized / invalid token |
| 403 | Forbidden / insufficient permissions |
| 404 | Resource not found |
| 422 | Unprocessable entity |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Rate Limiting

A sliding-window in-memory rate limiter is applied per IP. Default: 60 requests per 60 seconds. In production this should be replaced with a Redis-backed limiter.

## Versioning

The API is versioned under `/api/v1`. Breaking changes will be introduced under `/api/v2`.
