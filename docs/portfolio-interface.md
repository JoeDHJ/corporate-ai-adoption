# portfolio.v1 interface

Corporate AI Adoption owns company disclosure, coding and selected vacancy evidence. Other portfolio apps may consume these public snapshots without a live connection. It has no runtime dependency on Atlas, Career Fit or Impact.

The CLI writes a portfolio.v1.json envelope containing schema_version, version, as_of, sources, evidence, company_periods, labor, workforce, jobs, scenario, strategies, sensitivity, value_sensitivity, hiring_reference, evaluation and summary. Smaller JSON files and an evidence CSV are also exported.

Every public observation carries source_id, source_url, retrieved_at, source_vintage, geography, unit_of_observation, period, currency, price_year, schema_version and status where applicable. A null source_url for SCENARIO-BANK-01 means an internally defined fictional input, not a missing observed source. Currency and price year are null for counts/text. BLS wage medians use USD 2025, and scenario cash flows use constant USD 2026 assumptions.

Company identifiers use jurisdiction US, identifier type SEC-CIK, and a zero-padded native CIK, e.g. US:SEC-CIK:0000789019. source_native_id retains report identity. Occupation identifiers use SOC2018 plus source-native code. Skills include corporate-ai-role-tags v1.0 or corporate-ai-capabilities v1.0 and readable labels. No empirical occupation crosswalk or inferred transition probability is applied.

Evidence source_status=observed refers to the original disclosure; status=estimated refers to the coding. review_label/review_scope/review_reason are assistant judgments; classifier is a separate automatic method output. company_periods counts only selected reviewed spans. internal_deployment_evidence_ids=[] means none selected, with unknown issuer adoption.

Vacancy inputs require HTTPS public source URL, snapshot/retrieval dates, source vintage, geography, company_id, native job_id and title. skills can be null or a list/semicolon-separated string. Tagged skills require taxonomy and version. Counts are external labor-demand observations, never workforce stocks. Duplicate company/job/snapshot rows are rejected. Stable coverage across dates is an explicit prerequisite for any future trend estimate.

Scenario outputs include the full input dimensions, integer route counts, expected coverage, cost-only PV, NPV, payback and monthly cash flows. Infeasible results retain the reason and do not invent a cost or NPV. Zero is distinct from unknown/null.

Backward-incompatible field or unit changes require a new schema version. No silent sibling-source replacement or circular service dependency is permitted.

Four machine-readable JSON Schemas ship in corporate_ai/schemas: scenario, vacancy input, portfolio.v1 and scenario-output. Print one with `corporate-ai schema scenario`. Standard JSON Schema validation checks shape and field types; runtime checks additionally enforce cross-field timing, distinct skill IDs, source metadata and optimization constraints.

## Additive v2 extensions

The portfolio.v1 envelope retains all v1 fields and adds bank_case, bank_vacancies, vacancy_coverage, reliability, workflow_inputs, workflow and research_benchmark. Existing status/units conventions apply. bank_case contains 11 source records, coverage failures, reviewed statements, all candidate locations, independent-axis diagnostics and grouped text diagnostics. The bank vacancy taxonomy is corporate-ai-capabilities 2.0; do not pool it with legacy role tags. US in canonical company IDs denotes SEC registry jurisdiction, not incorporation nationality.

Workflow case files contain scenario and workflow objects plus optional results. Imports recalculate rather than trusting supplied results. Both objects must use the same currency and price year; browser cases are USD 2026. Values are workload-based and counted once; legacy per-capability benefit fields are excluded from staffing outputs in this context. The allocated staffing policy class and discrete scale choices define the optimum's scope. Snapshot consumers need no live service.

V2 also ships the workflow-case JSON Schema (`corporate-ai schema workflow-case`). Runtime validation additionally checks matching task IDs, units, dates and workload-derived constraints.
