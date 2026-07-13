# User Management, Birth Profiles & Birth Charts

## Overview

This module handles users, preferences, multiple birth profiles per user, generated birth charts, and their persistence.

## User Profile

A `User` is the application account. Each user gets:

- A `Role` (default `user`)
- Default `UserPreference` on registration
- One or more `BirthProfile` records
- One or more `Conversation` records
- Optional `Feedback` entries

### User Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Retrieve current user |
| PATCH | `/users/me` | Update name, email, preferences, timezone, country, theme, notifications, privacy |
| DELETE | `/users/me` | Soft-delete account |

## User Preferences

Preferences control UI and response behavior.

| Field | Default | Options |
|-------|---------|---------|
| preferred_language | `en` | en, hi, sa, etc. |
| preferred_explanation_depth | `balanced` | brief, balanced, detailed |
| preferred_astrology_school | `parashari` | parashari, jaimini, etc. |
| preferred_chart_style | `north_indian` | north_indian, south_indian |
| citation_mode | `inline` | inline, footnote |
| dark_mode | `false` | boolean |
| units | `metric` | metric, imperial |
| timezone | `UTC` | IANA timezone |
| country | `null` | ISO country or name |
| theme_preference | `system` | system, light, dark |

## Birth Profiles

Users can store multiple birth profiles (self, spouse, children, clients).

### Required fields

- `profile_name`
- `relationship`
- `date_of_birth`

### Optional fields

- `time_of_birth`
- `birth_place`
- `latitude`, `longitude`
- `timezone`
- `accuracy_level`
- `notes`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/profiles` | Create profile |
| GET | `/profiles` | List profiles |
| GET | `/profiles/{id}` | Get profile |
| PATCH | `/profiles/{id}` | Update profile |
| DELETE | `/profiles/{id}` | Soft-delete profile |

## Birth Charts

A `BirthChart` is generated for a profile and stores the computed chart data as JSON. Related tables (`planet_positions`, `house_positions`, `dashas`) persist the chart in normalized form.

```python
from divyadrishti.services.birth_chart_service import BirthChartService

chart_service = BirthChartService(db)
chart = chart_service.store_chart(
    profile_id=profile.id,
    chart_type="rashi",
    chart_data={...},
)
```

## Data Ownership

- Users can only access their own profiles, conversations, and feedback.
- Admins and super admins can access all resources.
- Soft deletes keep records for audit and restore.

## Repository Layer

| Repository | Purpose |
|------------|---------|
| `UserRepository` | User and role CRUD |
| `PreferenceRepository` | User preferences |
| `BirthProfileRepository` | Birth profiles |
| `ConversationRepository` | Conversations and messages |
| `FeedbackRepository` | Feedback |

## Service Layer

| Service | Purpose |
|---------|---------|
| `AuthenticationService` | Register, login, refresh, logout |
| `UserService` | User profile updates and deletion |
| `PreferenceService` | Preference retrieval and updates |
| `BirthProfileService` | Birth profile management |
| `BirthChartService` | Chart storage and retrieval |
| `ConversationService` | Conversation and message management |
| `FeedbackService` | Feedback capture |
| `AuthorizationService` | Permission checks |

## Testing

- Unit tests: `tests/unit/auth/test_services.py`, `tests/unit/auth/test_repositories.py`
- Integration tests: `tests/integration/test_auth.py`
- Run all tests with `pytest`.
