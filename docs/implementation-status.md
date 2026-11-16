# Implementation status

## Scope and baseline — 2026-11-16

Keep: MIT license, repository identity, development brief. Baseline main was clean and contained no application or analysis. Work is on `codex/flagship-v1`.

Add: official multi-period company corpus, evidence taxonomy and classifier comparison, official occupational demand benchmarks, constrained workforce investment model, Python CLI, offline dashboard, portfolio.v1 snapshots, executive deliverables and employer evidence matrix.

Validation: arithmetic and malformed-input tests; built-wheel clean installation; browser interaction, exports and responsive screenshots; independent read-only review; scoped fixes; GitHub CI and release.

## Progress

- Read shared and repository briefs and applicable owner standards.
- Completed official report discovery and access: twenty reports, ten firms, FY2023/FY2024.
- Firecrawl connected search is unavailable because its account has insufficient credits. Official-site HTTP retrieval and web search remain usable.

## Implemented and locally verified

- 60 exact, reviewed spans with source locators, taxonomy, scope and actual classifier evaluation.
- Global company employment composition, six same-vintage BLS occupation benchmarks and three official employer JDs; no invented historical vacancy panel.
- Reusable CSV/JSON vacancy adapter preserving missing versus zero and taxonomy boundaries.
- Constrained workforce solver, cash flows, NPV/payback, attainment/value sensitivity and clear infeasibility reasons.
- Five-module offline dashboard, export preparation, seven original-size screenshots and 90/180/365-day management deliverables.
- portfolio.v1 outputs, complete standalone scenario exports and four bundled JSON Schemas.
- 37 checks plus cross-runtime and CSV checks passed. A clean built-wheel install generated the complete case without runtime dependencies.
- Two independent read-only reviews and targeted re-reviews closed all findings; see [review-log.md](review-log.md).

## Publication

The reviewed implementation is ready for the codex/ feature-branch PR, GitHub CI matrix and v1.0.0 release. Remote publication results are recorded in the release and Actions pages after completion.
