# Frontend Architecture

## Overview

The DivyaDrishti frontend is a Next.js 15 application built with React 19, TypeScript, Tailwind CSS, and shadcn/ui. It is designed to be modular, accessible, and theme-aware, forming a production-ready foundation for all future features.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Next.js 15 | App Router, SSR, SSG, and API routes |
| React 19 | UI library |
| TypeScript | Type safety and strict mode |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Headless, accessible UI primitives |
| Framer Motion | Subtle animations |
| React Hook Form | Form state management |
| Zod | Schema validation |
| TanStack Query | Server state management |
| Lucide React | Icons |
| Vitest | Unit testing |
| React Testing Library | Component testing |
| Playwright | End-to-end testing |

## Folder Structure

```text
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/             # Authentication route group
│   ├── (dashboard)/        # Dashboard route group
│   ├── (admin)/            # Admin route group
│   ├── maintenance/        # Maintenance page
│   ├── globals.css         # Global styles + theme variables
│   ├── layout.tsx          # Root layout + providers
│   ├── page.tsx            # Placeholder home page
│   ├── loading.tsx         # Global loading UI
│   ├── error.tsx           # Global error boundary
│   ├── not-found.tsx       # 404 page
│   └── global-error.tsx    # Top-level error boundary
├── components/
│   ├── ui/                 # Reusable design system components
│   └── layout/             # Layout components (shell, navbar, sidebar, footer)
├── features/               # Self-contained feature modules
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities and shared helpers
├── services/               # API service functions
├── types/                  # Shared TypeScript types
├── styles/                 # Global styles documentation
├── providers/              # Global context providers
├── config/                 # Site and app configuration
├── constants/              # App constants and enums
├── utils/                  # Formatting and helpers
├── assets/                 # Imported static assets
├── public/                 # Public static files
└── tests/                  # Vitest + Playwright tests
```

## Component Philosophy

- **Composition over configuration**: Components accept `children`, `className`, and `asChild` where possible.
- **Small, reusable primitives**: UI components live in `components/ui` and know nothing about business logic.
- **Feature modules**: `features/` groups domain-specific components, hooks, schemas, and services.
- **Accessibility**: All interactive components use Radix primitives, include ARIA attributes, and support keyboard navigation.
- **Theme-aware**: Components use `bg-card`, `text-foreground`, and other CSS variables so they adapt to light and dark themes.

## Theme Architecture

- Theme variables are declared in `app/globals.css` and mapped to `hsl()` values.
- `tailwind.config.ts` extends Tailwind with custom colors and animations.
- `next-themes` provides `light`, `dark`, and `system` modes.
- `ThemeToggle` lets users switch themes.
- `ThemeProvider` wraps the app in `providers/index.tsx`.

## State Management

- **Local UI state**: React `useState`/`useReducer` and custom hooks.
- **Server state**: TanStack Query (via `QueryProvider`).
- **Global context**: `ThemeProvider`, `AuthProvider`, `SettingsProvider`, `ToastProvider`.
- **Form state**: React Hook Form + Zod.

## Responsive Strategy

- Mobile-first Tailwind breakpoints.
- `useMediaQuery` hook for JS-based responsive behavior.
- `Sidebar` is hidden on mobile and replaced by a `Drawer` triggered from the `Navbar`.
- Touch-friendly targets (min 44px) and large click surfaces.

## Layout System

| Layout | Responsibility |
|--------|----------------|
| `AppShell` | Application shell with navbar, sidebar, and footer |
| `AuthLayout` | Centered authentication card layout |
| `DashboardLayout` | AppShell for dashboard views |
| `AdminLayout` | AppShell for admin views |
| `PageContainer` | Consistent page padding and max-width |

## Error Handling

- `error.tsx` catches errors in the `app` segment.
- `global-error.tsx` catches top-level errors.
- `not-found.tsx` handles 404s.
- `loading.tsx` shows skeletons during suspense.
- `ErrorState`, `EmptyState`, and `Skeleton` components are reusable across the app.

## Testing Strategy

- **Unit tests** with Vitest and React Testing Library.
- **E2E tests** with Playwright across desktop and mobile viewports.
- `tests/setup.ts` stubs `matchMedia` and imports `jest-dom` matchers.
