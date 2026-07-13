# DivyaDrishti Frontend

This directory contains the Next.js 15 frontend application for DivyaDrishti.

## Stack

- Next.js 15
- React 19
- TypeScript (strict mode)
- Tailwind CSS
- shadcn/ui
- Framer Motion
- React Hook Form
- Zod
- TanStack Query
- Lucide React

## Structure

```text
frontend/
├── app/          # Next.js App Router
├── components/   # React components
│   ├── ui/       # Design system primitives
│   └── layout/   # Layout components
├── features/     # Feature modules
├── hooks/        # Custom React hooks
├── lib/          # Utilities and API client
├── services/     # API service functions
├── types/        # Shared TypeScript types
├── styles/       # Global styles documentation
├── providers/    # Global providers
├── config/       # App configuration
├── constants/    # App constants
├── utils/        # Formatting and helpers
├── assets/       # Imported static assets
├── public/       # Public static files
└── tests/        # Vitest + Playwright tests
```

## Getting Started

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run format` | Format with Prettier |
| `npm run test` | Run Vitest in watch mode |
| `npm run test:run` | Run Vitest once |
| `npm run test:e2e` | Run Playwright tests |

## Foundation

This is a frontend foundation. Business logic, backend API integration, chat, dashboard, authentication, admin, and report pages are not implemented yet.
