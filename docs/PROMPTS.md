# Prompt Management

## Prompt Versions

All prompt templates are versioned through `prompts/manifest.json`. The `PromptManager` exposes the version of each loaded template. The manifest is the source of truth for version tracking and variable lists.

## Template Format

Prompts are stored as Markdown files in `prompts/`. Each file contains:

- Purpose and relevant factors
- Variable list under `## Variables`
- Jinja2 template under `## Template`

```markdown
# Career Prompt

## Purpose

Generate responses for career questions.

## Variables

- `career_indicators`
- `strengths`
- `timing_estimate`

## Template

```text
The user is asking about their career. Based on the following indicators:
{{ career_indicators }}

Strengths: {{ strengths }}
Timing: {{ timing_estimate }}
```
```

## Variables

Variables are declared in the `## Variables` section. The `PromptManager` validates that all declared variables are supplied before rendering.

## Prompt Registry

| Prompt | File | Version | Variables |
|--------|------|---------|-----------|
| system | `prompts/system.md` | 1.0.0 | user_name, chart_summary, reasoning_trace, conversation_history, user_question |
| career | `prompts/career.md` | 1.0.0 | career_indicators, strengths, timing_estimate |
| marriage | `prompts/marriage.md` | 1.0.0 | marriage_indicators, timing, compatibility |
| finance | `prompts/finance.md` | 1.0.0 | finance_indicators, sources_of_income, timing |
| health | `prompts/health.md` | 1.0.0 | health_indicators, vulnerable_areas, remedies |
| education | `prompts/education.md` | 1.0.0 | education_indicators, fields, timing |
| relationship | `prompts/relationship.md` | 1.0.0 | relationship_indicators, compatibility, timing |
| personality | `prompts/personality.md` | 1.0.0 | personality_indicators, strengths, challenges |
| report_generation | `prompts/report_generation.md` | 1.0.0 | report_type, chart_summary, sections |

## Testing

Prompts are tested by the `PromptManager` test suite:

- Load each prompt
- Validate required variables
- Render with sample variables
- Check for the presence of safety instructions

## A/B Testing

Future: support prompt variants by loading different manifest files or directories.

## Rollback

Rollback to a previous prompt version by restoring the `prompts/manifest.json` entry and the associated Markdown file from version control.
