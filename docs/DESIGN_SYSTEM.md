# Design System

## Visual Identity

DivyaDrishti is designed to feel premium, modern, elegant, calm, minimal, and trustworthy. The palette is inspired by Indian aesthetics but rendered with a contemporary, clean approach.

## Colors

### Primary Palette

| Color | Tailwind Key | Usage |
|-------|--------------|-------|
| Deep Indigo | `indigo-600` / `indigo-700` | Primary brand, buttons, links, focus rings |
| Soft Gold | `gold-400` / `gold-500` | Secondary accents, highlights, badges |
| Ivory | `ivory` | Light mode background, card surfaces |
| Slate Gray | `slate-400` / `slate-500` | Neutral text, borders, muted elements |

### Accent

| Color | Tailwind Key | Usage |
|-------|--------------|-------|
| Saffron | `saffron-500` / `saffron-600` | Accent states, call-to-actions, warm highlights |

### Semantic Colors

| Token | Light Mode | Dark Mode |
|-------|------------|-----------|
| `--background` | Ivory | Deep slate |
| `--foreground` | Near-black | Soft white |
| `--primary` | Deep Indigo | Soft Indigo |
| `--secondary` | Soft Gold | Soft Gold |
| `--accent` | Saffron | Saffron |
| `--muted` | Light slate | Dark slate |
| `--border` | Light slate | Dark slate border |
| `--destructive` | Red 600 | Red 500 |

## Typography

- **Sans (body)**: `Inter` — clean, readable, modern.
- **Display (headings)**: `Playfair Display` — elegant, premium, Indian-inspired refinement.
- **Hierarchy**: H1 (3rem), H2 (2.25rem), H3 (1.5rem), H4 (1.25rem), body (1rem), small (0.875rem).
- **Line height**: `leading-relaxed` for body, `leading-tight` for headings.
- **Letter spacing**: `tracking-tight` for display headings.

## Spacing & Radius

- **Base radius**: `--radius: 0.75rem` (12px)
- **Component radius**: `rounded-md` (6px), `rounded-lg` (8px), `rounded-xl` (12px)
- **Page padding**: `px-4` mobile, `px-6` tablet, `px-8` desktop
- **Section spacing**: `py-12` mobile, `py-16` desktop

## Shadows

- `shadow-card` — card surfaces
- `shadow-soft` — hover lifts
- `shadow-elevated` — modals, drawers

## Component Inventory

| Component | File | Purpose |
|-----------|------|---------|
| Button | `components/ui/button.tsx` | Primary action control with variants |
| Card | `components/ui/card.tsx` | Content containers |
| Badge | `components/ui/badge.tsx` | Status labels |
| Input | `components/ui/input.tsx` | Text input |
| Textarea | `components/ui/textarea.tsx` | Multi-line text input |
| Select | `components/ui/select.tsx` | Dropdown selection |
| Combobox | `components/ui/combobox.tsx` | Searchable dropdown |
| Dialog | `components/ui/dialog.tsx` | Modal dialogs |
| Drawer | `components/ui/drawer.tsx` | Mobile bottom sheets |
| Tabs | `components/ui/tabs.tsx` | Tab navigation |
| Accordion | `components/ui/accordion.tsx` | Collapsible content |
| Tooltip | `components/ui/tooltip.tsx` | Hover hints |
| Toast | `components/ui/toast.tsx` / `sonner.tsx` | Notification system |
| Alert | `components/ui/alert.tsx` | Inline messages |
| Avatar | `components/ui/avatar.tsx` | User avatars |
| Breadcrumb | `components/ui/breadcrumb.tsx` | Navigation hierarchy |
| Sidebar | `components/layout/sidebar.tsx` | Desktop sidebar |
| Navbar | `components/layout/navbar.tsx` | Top navigation |
| Footer | `components/layout/footer.tsx` | Page footer |
| Skeleton | `components/ui/skeleton.tsx` | Loading placeholders |
| Empty State | `components/ui/empty-state.tsx` | Empty content |
| Error State | `components/ui/error-state.tsx` | Error displays |
| Page Container | `components/layout/page-container.tsx` | Page wrapper |
| Section | `components/ui/section.tsx` | Section layout |
| Theme Toggle | `components/ui/theme-toggle.tsx` | Light / dark toggle |

## Component Variants

### Button

- `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`
- Sizes: `default`, `sm`, `lg`, `icon`
- Supports `isLoading` and `asChild`

### Card

- `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`
- Subtle hover shadow lift

### Input / Textarea

- Focus ring with `ring-primary`
- Disabled states
- Placeholder color from `muted-foreground`

### Select

- Radix Select primitive
- `SelectTrigger`, `SelectValue`, `SelectContent`, `SelectItem`, `SelectGroup`, `SelectLabel`, `SelectSeparator`

### Dialog

- Radix Dialog primitive
- `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter`

### Drawer

- `vaul` bottom sheet
- Mobile-first navigation and forms

## Accessibility

- All form inputs have `focus-visible` rings.
- All interactive elements have `aria-label` or associated text.
- Color contrast meets WCAG AA minimums.
- Reduced motion is respected via `prefers-reduced-motion` (Tailwind `motion-reduce:`).
- Keyboard navigable components via Radix primitives.

## Animations

- Page transitions, card hovers, and dialog entrances use `framer-motion`.
- Tailwind animations are limited to `fade-in`, `slide-up`, `shimmer`, and `accordion`.
- Theme switching is smooth via `next-themes` and CSS transitions.

## Theme Switching

Use the `ThemeToggle` component or `useTheme` from `next-themes`.

```tsx
import { ThemeToggle } from "@/components/ui/theme-toggle";

<ThemeToggle />
```

Light and dark themes are fully defined in `app/globals.css`.
