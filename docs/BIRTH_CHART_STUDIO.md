# Birth Chart Studio

## Overview

The Birth Chart Studio is the interactive Vedic astrology workspace for DivyaDrishti. It renders SVG charts, exposes every chart element (planets, houses, signs, nakshatras, yogas, doshas, dashas, transits) for exploration, and integrates with the Reasoning Engine, Explainability Engine, Knowledge Engine, and AI Conversation Engine.

## Objectives

- Render real, computed D1 (Rashi) and D9 (Navamsa) charts with SVG.
- Provide interactive exploration of every chart element.
- Surface context-aware insights for questions like career, marriage, finance, and health.
- Integrate with existing backend engines for reasoning, explainability, and knowledge.
- Support responsive layouts, keyboard navigation, and accessibility.

## Architecture

### Backend

```
backend/src/divyadrishti/astrology/
├── __init__.py              # Exports generator and models
├── constants.py             # Vedic constants (signs, planets, nakshatras, dignities, dashas, yogas)
├── models.py                # Pydantic models for ChartData, PlanetPosition, HousePosition, etc.
├── utils.py                 # Longitude/sign/nakshatra/house helpers and datetime parsing
├── generator.py             # BirthChartGenerator using pyswisseph
├── dasha.py                 # Vimshottari dasha calculation
├── yoga.py                  # Yoga detection
├── dosha.py                 # Dosha detection
└── aspects.py               # Planetary aspect calculation
```

- `BirthChartGenerator` uses `pyswisseph` with Lahiri ayanamsa and Moshier fallback ephemeris.
- It computes D1 and D9 positions, houses, nakshatras, dignity, retrograde, combustion, dashas, yogas, doshas, and aspects.
- `BirthChartService.generate_chart` creates and stores D1 and D9 charts.
- `StudioService` fetches a stored chart, runs `AstrologicalReasoningEngine` and `ExplainabilityEngine`, and produces `ChartStudioDetail` with visualizations and context-aware insights.

### API Endpoints

- `POST /api/v1/profiles/{id}/charts?chart_type=rashi` — generate and store a chart.
- `GET /api/v1/profiles/{id}/charts/latest?chart_type=rashi` — latest chart for a profile.
- `GET /api/v1/profiles/{id}/charts/{chart_type}` — chart by type.
- `GET /api/v1/charts/{id}` — chart by ID.
- `GET /api/v1/charts/{id}/studio?question=...` — full studio detail.
- `POST /api/v1/charts/{id}/analyze` — analyze with a question.
- `GET /api/v1/charts/{id}/search?q=...` — search chart elements.

### Frontend

```
frontend/app/(dashboard)/studio/page.tsx
frontend/components/studio/
├── studio-page.tsx          # Main studio page, chart type tabs, search, layout
├── birth-chart-svg.tsx      # Interactive South-Indian-style SVG chart
├── planet-panel.tsx         # Selected planet details
├── house-panel.tsx          # Selected house details
├── nakshatra-panel.tsx      # Selected nakshatra details
├── dasha-panel.tsx          # Vimshottari dasha timeline
├── yoga-panel.tsx           # Yoga list
├── dosha-panel.tsx          # Dosha list
└── insight-panel.tsx        # Context-aware question + highlights
```

- `StudioPage` uses `useSettings().currentProfileId`, `useLatestProfileChart`, and `useStudio`.
- It auto-generates a chart if none exists for the selected profile.
- `BirthChartSvg` renders a 4x3 grid of fixed signs with planets, supports click/keyboard selection.
- The right panel switches between `PlanetPanel`, `HousePanel`, and `NakshatraPanel` based on selection.
- `InsightPanel` lets the user ask a question and re-runs `useAnalyzeChart` to update highlights.

## Chart Rendering

### SVG Architecture

- `BirthChartSvg` uses a 4x3 grid of fixed signs (South Indian style).
- Each cell is an SVG `<g>` with a rounded rectangle, sign symbol, house number, and planet circles.
- Planets are rendered as colored circles with their 2-letter symbols.
- Lagna sign is highlighted with a primary stroke.
- Selected element has an additional ring and fill.
- The chart is responsive via `viewBox` and `w-full h-auto`.

### Interaction Model

- Click a cell → select sign.
- Click a planet → select planet.
- Click a house number → select house.
- Keyboard: `Tab` to navigate, `Enter`/`Space` to select.
- `onSelect` callback updates the `StudioPage` state and renders the appropriate detail panel.

## Context Synchronization

- `StudioPage` uses TanStack Query to keep chart data and studio detail in sync.
- `useGenerateChart` invalidates the charts query after generation.
- `useStudio` refetches when the selected chart changes or when `chartType` changes.
- `InsightPanel` stores a local `insight` state and updates it after `analyzeChart` completes.

## Reasoning / Explainability Integration

- `StudioService` converts `ChartData` to `AstrologicalChart` using `to_astrological_chart`.
- It runs `AstrologicalReasoningEngine.reason` for the user's question and `ExplainabilityEngine.explain`.
- `explainability_report.visualizations` are included in the `StudioChartDetail` payload.
- `InsightPanel` uses `StudioService._build_insight` to highlight relevant planets/houses/yogas/dashas based on the topic.

## Chart Types

- D1 (Rashi): primary natal chart.
- D9 (Navamsa): relationship/spiritual chart.
- The architecture supports future D10 (Dasamsa), D7 (Saptamsa), D60 (Shashtiamsa), Moon Chart, and Transit Chart via `VargaChart` and `generate_varga`.
- Current UI offers a `Tabs` switcher between D1 and D9.

## Performance Strategy

- SVG is rendered without external charting libraries.
- `useMemo` groups planets by sign and computes house numbers.
- TanStack Query caches chart data and studio detail.
- Panels are conditionally rendered based on selection.
- `react-virtuoso` can be introduced for long dasha/yoga/dosha lists if needed.

## Accessibility

- SVG has `role="img"` and `aria-label`.
- Interactive cells are focusable and keyboard-activatable.
- House numbers and planets are labeled.
- Color is not the only identifier: planet symbols are text inside circles.
- High contrast is supported via Tailwind dark mode and `text-white` planet labels.

## Testing

- Unit tests for `BirthChartGenerator` calculation helpers.
- Component tests for `BirthChartSvg` interaction and panel rendering.
- Integration tests for `StudioService` and studio routes.
- Playwright tests for the `/studio` page flow.

## Future Work

- Implement North Indian and Western chart styles.
- Add D10, D7, D60, Moon Chart, and Transit Chart generation.
- Add more yoga/dosha detectors.
- Add richer graph visualizations (planet/house/evidence graphs) using SVG or D3.
- Add chart export and comparison features.
