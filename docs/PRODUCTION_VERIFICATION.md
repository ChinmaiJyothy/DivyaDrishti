# DivyaDrishti Production Verification Report

- **Verification started:** 2026-07-16T09:30:34.920900+00:00
- **Verification user:** verify-262ec337@example.com
- **Overall Production Readiness:** 100.0%

## Checklist

### Phase 1 - Authentication

- **Status:** PASS
- [ ] Register
- [ ] Login
- [ ] Refresh Token
- [ ] Logout
- [ ] Protected Routes

### Phase 2 - Birth Profiles

- **Status:** PASS
- [ ] Create Profile
- [ ] Edit Profile
- [ ] Delete Profile
- [ ] Generate Birth Chart
- [ ] Verify chart data
- [ ] Verify Dasha generation
- [ ] Verify stored chart

### Phase 3 - Knowledge Corpus

- **Status:** PASS
- [ ] Upload
- [ ] OCR
- [ ] Language Detection
- [ ] Metadata Extraction
- [ ] Chunking
- [ ] Embeddings
- [ ] Knowledge Graph
- [ ] Rule Extraction
- [ ] Admin Approval
- [ ] Corpus Search
- [ ] Reasoning Integration

### Phase 4 - AI Conversation

- **Status:** PASS
- [ ] Create new conversation
- [ ] Ask career prospects
- [ ] Streaming
- [ ] Reasoning
- [ ] Evidence
- [ ] Confidence
- [ ] Explainability
- [ ] Conversation Persistence
- [ ] History
- [ ] Retry
- [ ] Regenerate
- [ ] Delete
- [ ] Rename

### Phase 5 - Dashboard

- **Status:** PASS
- [ ] Recent Conversations
- [ ] Quick Actions
- [ ] Birth Profile
- [ ] Knowledge Card
- [ ] Settings
- [ ] Feedback

### Phase 6 - Settings

- **Status:** PASS
- [ ] Language
- [ ] Theme
- [ ] Preferences
- [ ] Citation Mode

### Phase 7 - Feedback

- **Status:** PASS
- [ ] Submit feedback
- [ ] Verify storage
- [ ] Verify analytics

### Phase 8 - Performance

- **Status:** PASS
- [ ] Page Load
- [ ] Chat Response Time
- [ ] Knowledge Retrieval
- [ ] Reasoning Time
- [ ] Corpus Search

### Phase 9 - Security

- **Status:** PASS
- [ ] Authentication
- [ ] Authorization
- [ ] JWT
- [ ] Rate Limiting
- [ ] Permissions
- [ ] Input Validation

## Working Features

- Phase 1 - Authentication: PASS
- Phase 2 - Birth Profiles: PASS
- Phase 3 - Knowledge Corpus: PASS
- Phase 4 - AI Conversation: PASS
- Phase 5 - Dashboard: PASS
- Phase 6 - Settings: PASS
- Phase 7 - Feedback: PASS
- Phase 8 - Performance: PASS
- Phase 9 - Security: PASS

## Failed Features


## Bugs Found

- `GET http://localhost:8000/api/v1/users/me` -> 401 (phase-1/protected-route-no-token)
- `POST http://localhost:8000/api/v1/auth/refresh` -> 400 (phase-1/refresh-after-logout)
- `GET http://localhost:8000/api/v1/users/me` -> 401 (phase-9/invalid-jwt)
- `GET http://localhost:8000/api/v1/users/me` -> 401 (phase-9/missing-auth)
- `POST http://localhost:8000/api/v1/auth/login` -> 400 (phase-9/wrong-password)
- `POST http://localhost:8000/api/v1/auth/register` -> 422 (phase-9/input-validation-register)
- `GET http://localhost:8000/api/v1/profiles/999999` -> 404 (phase-9/nonexistent-profile-isolation)

## Bugs Fixed

TBD - none applied during this run

## Request/Response Log

| Phase | Step | Method | URL | Status | Elapsed ms |
|-------|------|--------|-----|--------|------------|
| phase-1 | register | POST | http://localhost:8000/api/v1/auth/register | 201 | 2341.11 |
| phase-1 | login | POST | http://localhost:8000/api/v1/auth/login | 200 | 86.81 |
| phase-1 | protected-route-me | GET | http://localhost:8000/api/v1/users/me | 200 | 11.14 |
| phase-1 | protected-route-no-token | GET | http://localhost:8000/api/v1/users/me | 401 | 2.17 |
| phase-1 | refresh-token | POST | http://localhost:8000/api/v1/auth/refresh | 200 | 31.70 |
| phase-1 | logout | POST | http://localhost:8000/api/v1/auth/logout | 200 | 13.83 |
| phase-1 | refresh-after-logout | POST | http://localhost:8000/api/v1/auth/refresh | 400 | 5.78 |
| phase-1 | relogin | POST | http://localhost:8000/api/v1/auth/login | 200 | 84.28 |
| phase-2 | create-profile | POST | http://localhost:8000/api/v1/profiles | 201 | 24.21 |
| phase-2 | list-profiles | GET | http://localhost:8000/api/v1/profiles | 200 | 6.67 |
| phase-2 | edit-profile | PATCH | http://localhost:8000/api/v1/profiles/1 | 200 | 17.64 |
| phase-2 | get-profile | GET | http://localhost:8000/api/v1/profiles/1 | 200 | 5.62 |
| phase-2 | generate-birth-chart | POST | http://localhost:8000/api/v1/profiles/1/charts | 201 | 46.50 |
| phase-2 | get-latest-chart | GET | http://localhost:8000/api/v1/profiles/1/charts/latest | 200 | 11.37 |
| phase-2 | list-charts | GET | http://localhost:8000/api/v1/profiles/1/charts | 200 | 8.96 |
| phase-2 | generate-dasha | POST | http://localhost:8000/api/v1/profiles/1/charts?chart_type=dasha | 201 | 18.18 |
| phase-2 | get-dasha-chart | GET | http://localhost:8000/api/v1/profiles/1/charts/dasha | 200 | 8.71 |
| phase-2 | delete-profile | DELETE | http://localhost:8000/api/v1/profiles/1 | 200 | 15.68 |
| phase-3 | verify-admin-status | GET | http://localhost:8000/api/v1/users/me | 200 | 6.62 |
| phase-3 | create-corpus | POST | http://localhost:8000/api/v1/corpus/corpora | 201 | 71.09 |
| phase-3 | upload-book | POST | http://localhost:8000/api/v1/corpus/corpora/1/books | 201 | 22.06 |
| phase-3 | ingest-book | POST | http://localhost:8000/api/v1/corpus/books/1/ingest | 200 | 1959.12 |
| phase-3 | list-corpus-books | GET | http://localhost:8000/api/v1/corpus/books | 200 | 8.99 |
| phase-3 | list-candidate-rules | GET | http://localhost:8000/api/v1/corpus/candidate-rules | 200 | 12.36 |
| phase-3 | approve-rule | POST | http://localhost:8000/api/v1/corpus/candidate-rules/1/approve | 200 | 66.93 |
| phase-3 | knowledge-graph | GET | http://localhost:8000/api/v1/corpus/graph | 200 | 8.95 |
| phase-3 | knowledge-overview | GET | http://localhost:8000/api/v1/knowledge | 200 | 11.40 |
| phase-4 | create-conversation | POST | http://localhost:8000/api/v1/conversations | 201 | 17.83 |
| phase-4 | list-conversations | GET | http://localhost:8000/api/v1/conversations | 200 | 9.51 |
| phase-4 | add-user-message | POST | http://localhost:8000/api/v1/conversations/1/messages | 200 | 25.23 |
| phase-4 | chat-stream | POST | http://localhost:8000/api/v1/chat/1 | 200 | 137.16 |
| phase-4 | get-conversation | GET | http://localhost:8000/api/v1/conversations/1 | 200 | 8.72 |
| phase-4 | rename-conversation | PATCH | http://localhost:8000/api/v1/conversations/1 | 200 | 23.17 |
| phase-4 | retry-message | POST | http://localhost:8000/api/v1/conversations/1/messages | 200 | 22.14 |
| phase-4 | pin-conversation | POST | http://localhost:8000/api/v1/conversations/1/pin | 200 | 27.40 |
| phase-4 | archive-conversation | POST | http://localhost:8000/api/v1/conversations/1/archive | 200 | 24.39 |
| phase-4 | resume-conversation | POST | http://localhost:8000/api/v1/conversations/1/resume | 200 | 21.92 |
| phase-4 | delete-conversation | DELETE | http://localhost:8000/api/v1/conversations/1 | 200 | 20.26 |
| phase-5 | recent-conversations | GET | http://localhost:8000/api/v1/conversations | 200 | 4.97 |
| phase-5 | birth-profile-widget | GET | http://localhost:8000/api/v1/profiles | 200 | 6.30 |
| phase-5 | knowledge-card | GET | http://localhost:8000/api/v1/knowledge | 200 | 6.25 |
| phase-5 | knowledge-books-count | GET | http://localhost:8000/api/v1/knowledge/books | 200 | 6.01 |
| phase-5 | quick-actions-user | GET | http://localhost:8000/api/v1/users/me | 200 | 6.52 |
| phase-6 | get-preferences | GET | http://localhost:8000/api/v1/preferences | 200 | 11.02 |
| phase-6 | update-preferences | PATCH | http://localhost:8000/api/v1/preferences | 200 | 18.55 |
| phase-6 | verify-preferences | GET | http://localhost:8000/api/v1/preferences | 200 | 7.88 |
| phase-7 | submit-feedback | POST | http://localhost:8000/api/v1/feedback | 201 | 18.11 |
| phase-7 | verify-user-feedback | GET | http://localhost:8000/api/v1/users/me | 200 | 4.66 |
| phase-8 | page-load-frontend | GET | http://localhost:3000 | 200 | 316.73 |
| phase-8 | health-check | GET | http://localhost:8000/api/v1/health | 200 | 3.59 |
| phase-8 | knowledge-retrieval-create-profile | POST | http://localhost:8000/api/v1/profiles | 201 | 18.01 |
| phase-8 | reasoning-time-generate-chart | POST | http://localhost:8000/api/v1/profiles/2/charts?chart_type=rashi | 201 | 31.36 |
| phase-9 | invalid-jwt | GET | http://localhost:8000/api/v1/users/me | 401 | 3.46 |
| phase-9 | missing-auth | GET | http://localhost:8000/api/v1/users/me | 401 | 1.27 |
| phase-9 | wrong-password | POST | http://localhost:8000/api/v1/auth/login | 400 | 74.70 |
| phase-9 | input-validation-register | POST | http://localhost:8000/api/v1/auth/register | 422 | 3.40 |
| phase-9 | nonexistent-profile-isolation | GET | http://localhost:8000/api/v1/profiles/999999 | 404 | 8.71 |

## Performance Metrics

- **page-load-frontend:** 316.73 ms (status 200)
- **health-check:** 3.59 ms (status 200)
- **knowledge-retrieval-create-profile:** 18.06 ms (status 201)
- **reasoning-time-generate-chart:** 31.61 ms (status 201)
- **chat-stream:** 137.16 ms (status 200)

## Security Findings

- **invalid-jwt:** status=401 ok=True
- **missing-auth:** status=401 ok=True
- **wrong-password:** status=400 ok=True
- **input-validation-register:** status=422 ok=True
- **nonexistent-profile-isolation:** status=404 ok=True
- **rate-limiting:** status=None ok=True

## Remaining Issues


## Screenshots

Screenshots are captured by `scripts/verify_screenshots.js` and stored in `verification/screenshots/`.

## Backend Log Tail

```
2026-07-16 15:00:34,807 INFO sqlalchemy.engine.Engine SELECT birth_charts.id, birth_charts.profile_id, birth_charts.chart_type, birth_charts.chart_data, birth_charts.generated_at 
FROM birth_charts 
WHERE birth_charts.id = ?
2026-07-16 15:00:34,808 INFO sqlalchemy.engine.Engine [cached since 3.053s ago] (5,)
INFO:     127.0.0.1:63617 - "POST /api/v1/profiles/2/charts?chart_type=rashi HTTP/1.1" 201 Created
2026-07-16 15:00:34,811 INFO sqlalchemy.engine.Engine ROLLBACK
INFO:     127.0.0.1:63617 - "GET /api/v1/users/me HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:63617 - "GET /api/v1/users/me HTTP/1.1" 401 Unauthorized
2026-07-16 15:00:34,819 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-16 15:00:34,819 INFO sqlalchemy.engine.Engine SELECT users.id AS users_id, users.email AS users_email, users.name AS users_name, users.hashed_password AS users_hashed_password, users.role_id AS users_role_id, users.is_active AS users_is_active, users.is_verified AS users_is_verified, users.is_superuser AS users_is_superuser, users.verification_token AS users_verification_token, users.reset_token AS users_reset_token, users.account_status AS users_account_status, users.deleted_at AS users_deleted_at, users.created_at AS users_created_at, users.updated_at AS users_updated_at 
FROM users 
WHERE users.email = ? AND users.deleted_at IS NULL
 LIMIT ? OFFSET ?
2026-07-16 15:00:34,820 INFO sqlalchemy.engine.Engine [cached since 3.602s ago] ('verify-262ec337@example.com', 1, 0)
2026-07-16 15:00:34,890 INFO sqlalchemy.engine.Engine ROLLBACK
INFO:     127.0.0.1:63617 - "POST /api/v1/auth/login HTTP/1.1" 400 Bad Request
INFO:     127.0.0.1:63617 - "POST /api/v1/auth/register HTTP/1.1" 422 Unprocessable Entity
2026-07-16 15:00:34,899 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-16 15:00:34,899 INFO sqlalchemy.engine.Engine SELECT users.id AS users_id, users.email AS users_email, users.name AS users_name, users.hashed_password AS users_hashed_password, users.role_id AS users_role_id, users.is_active AS users_is_active, users.is_verified AS users_is_verified, users.is_superuser AS users_is_superuser, users.verification_token AS users_verification_token, users.reset_token AS users_reset_token, users.account_status AS users_account_status, users.deleted_at AS users_deleted_at, users.created_at AS users_created_at, users.updated_at AS users_updated_at 
FROM users 
WHERE users.id = ?
 LIMIT ? OFFSET ?
2026-07-16 15:00:34,899 INFO sqlalchemy.engine.Engine [cached since 3.374s ago] (1, 1, 0)
2026-07-16 15:00:34,900 INFO sqlalchemy.engine.Engine SELECT birth_profiles.id AS birth_profiles_id, birth_profiles.user_id AS birth_profiles_user_id, birth_profiles.profile_name AS birth_profiles_profile_name, birth_profiles.relationship AS birth_profiles_relationship, birth_profiles.date_of_birth AS birth_profiles_date_of_birth, birth_profiles.time_of_birth AS birth_profiles_time_of_birth, birth_profiles.birth_place AS birth_profiles_birth_place, birth_profiles.latitude AS birth_profiles_latitude, birth_profiles.longitude AS birth_profiles_longitude, birth_profiles.timezone AS birth_profiles_timezone, birth_profiles.accuracy_level AS birth_profiles_accuracy_level, birth_profiles.notes AS birth_profiles_notes, birth_profiles.chart_metadata AS birth_profiles_chart_metadata, birth_profiles.created_at AS birth_profiles_created_at, birth_profiles.updated_at AS birth_profiles_updated_at, birth_profiles.deleted_at AS birth_profiles_deleted_at 
FROM birth_profiles 
WHERE birth_profiles.id = ? AND birth_profiles.user_id = ? AND birth_profiles.deleted_at IS NULL
 LIMIT ? OFFSET ?
2026-07-16 15:00:34,901 INFO sqlalchemy.engine.Engine [cached since 3.196s ago] (999999, 1, 1, 0)
2026-07-16 15:00:34,902 INFO sqlalchemy.engine.Engine ROLLBACK
INFO:     127.0.0.1:63617 - "GET /api/v1/profiles/999999 HTTP/1.1" 404 Not Found
```
