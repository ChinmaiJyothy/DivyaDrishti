# Authentication & Security

## Overview

The Authentication module provides identity management, JWT access/refresh tokens, password hashing, role-based access control, session management, and password reset scaffolding.

## Security Stack

| Concern | Implementation |
|---------|----------------|
| Password hashing | Argon2id (`argon2-cffi`) |
| Access tokens | JWT (`python-jose`) with `HS256` |
| Refresh tokens | JWT with rotation, stored as SHA-256 hashes |
| Token transport | `Authorization: Bearer <token>` |
| Role/permission checks | `Role` model + `AuthorizationService` |
| Rate limiting | In-memory sliding-window (per IP) |
| Session tracking | `user_sessions` table |
| Password reset | Token-based scaffolding (email backend not wired) |

## Authentication Flow

```text
1. Client POST /auth/register
   -> Argon2id hash password
   -> Create user + role + default preferences
   -> Return access_token + refresh_token

2. Client POST /auth/login
   -> Verify Argon2id hash
   -> Create access_token + refresh_token
   -> Store refresh_token hash with expiry

3. Client uses access_token in Authorization header
   -> /users/me, /profiles, /conversations, etc.

4. Access token expires
   -> Client POST /auth/refresh with refresh_token
   -> Revoke old refresh token
   -> Issue new access_token + refresh_token

5. Logout
   -> Client POST /auth/logout with refresh_token
   -> Mark refresh token revoked
```

## Token Configuration

Settings are loaded from `SECRET_KEY`, `DATABASE_URL`, and `cors_origins` in `backend/.env`.

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | required | JWT signing key (min 16 chars) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | 10080 | Refresh token lifetime (7 days) |

## Password Reset Flow

1. Client POST `/auth/request-password-reset` with email.
2. Server generates a `reset_token` and stores it on the user.
3. Email service stub queues the reset email.
4. Client POST `/auth/reset-password` with `token` and `new_password`.
5. Server hashes the new password and clears `reset_token`.

## Email Verification

1. User registers; `verification_token` is generated.
2. Email service stub queues the verification email.
3. User clicks link; client POST `/auth/verify-email` with `token`.
4. Server sets `is_verified = true` and clears `verification_token`.

## Role-Based Access Control

Default roles: `user`, `researcher`, `admin`, `super_admin`.

Permissions are stored as a comma-separated list on `roles.permissions`. The `AuthorizationService` provides helpers:

- `is_admin(user)`
- `is_researcher_or_above(user)`
- `can_access_resource(user, resource_user_id)`
- `check_permission(user, permission)`

FastAPI dependencies:

- `get_current_user`
- `require_admin`
- `require_role("admin", "super_admin")`

## Middleware

`PermissionMiddleware` validates tokens, sets `request.state.user_id`, and applies rate limits. Public paths are whitelisted for `/auth/*` and `/health`.

## Testing

Run tests:

```bash
cd backend
pytest
```

Security-specific tests live in `tests/unit/auth/`.
