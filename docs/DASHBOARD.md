# Dashboard Implementation

## Overview

The dashboard is the central workspace for authenticated users. It surfaces birth profiles, recent conversations, reports, and knowledge-library activity, and provides quick actions to start new readings.

## Entry Point

The dashboard is served at the root route `/` by `frontend/app/(dashboard)/page.tsx`. The `DashboardLayout` is applied to the `(dashboard)` route group and wraps all pages in a responsive shell with sidebar, top navigation, context panel, and mobile bottom navigation.

## Layout

- `DashboardLayout` (`components/layout/dashboard-layout.tsx`) composes:
  - `Navbar` — top bar with search, language selector, theme toggle, notifications, and profile menu
  - `Sidebar` — collapsible desktop navigation with active-route highlighting
  - `MobileNav` — drawer-based navigation for small screens
  - `BottomNav` — mobile quick-access tabs
  - `ContextPanel` — right-side panel showing the currently selected birth profile

## Dashboard Components

Components live in `frontend/components/dashboard/`:

| Component | Responsibility |
|-----------|----------------|
| `DashboardHeader` | Greeting and workspace overview |
| `DashboardStats` | Quick counts for profiles, conversations, reports, and knowledge |
| `QuickActions` | Action grid to ask questions, generate reports, and upload books |
| `RecentConversations` | Latest conversations with preview/archive/delete |
| `RecentReports` | Latest reports with download/delete |
| `KnowledgeCard` | Knowledge library books and upload dialog |
| `BirthProfileCard` | Current profile selector and creation dialog |
| `PlanetaryOverview` | Grid of planetary positions from the latest chart |

## Routing

The `(dashboard)` route group contains:

- `/` — Dashboard
- `/ask` — Ask DivyaDrishti
- `/profiles` — Birth profiles management
- `/charts` — Birth chart / planetary overview
- `/conversations` — Conversation history
- `/reports` — Report history
- `/knowledge` — Knowledge library
- `/settings` — User preferences
- `/profile` — User profile
- `/feedback` — Feedback form
- `/admin` — Admin-only knowledge management

## API & State

- API calls are organized under `frontend/services/`.
- TanStack Query hooks live under `frontend/hooks/`.
- `AuthProvider` handles authentication state, token persistence, and `getMe`.
- `SettingsProvider` tracks global UI state, including the current birth profile.
- `QueryProvider` wraps the app in a `QueryClient` with `staleTime` and `refetchOnWindowFocus` defaults.

## Quick Actions

- **Ask a Question** — opens a dialog to create a new conversation
- **Generate Horoscope** — creates a `full_horoscope` report
- **Career / Marriage / Finance / Health / Compatibility** — creates a new conversation in that domain
- **Upload Knowledge Book** — admin-only upload to the knowledge library

## Loading & Empty States

- `Skeleton` placeholders are shown while TanStack Query fetches initial data.
- `EmptyState` components are used for lists with no data.
- `ErrorState` (and `toast` notifications) surface errors for mutations.
- Mutations invalidate affected queries on success so the dashboard refreshes.

## Responsive Behavior

- On desktop, the sidebar and context panel are visible.
- The sidebar collapses to icon-only mode.
- The context panel can be toggled from the navbar.
- On mobile, the sidebar is hidden and replaced by a drawer and a bottom tab bar.
