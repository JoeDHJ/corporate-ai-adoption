# Measurement, model and reproducibility
Version 1.0.0 · 16 November 2026

## Public inputs and permitted scope

Twenty official annual reports/10-Ks cover ten US-listed issuers in FY2023 and FY2024. The peer group is purposive: enterprise technology suppliers and banks using knowledge-intensive workflows. This is an early-adoption retrospective, not a current market census. Fiscal labels are source-native; year ends differ.

The package includes three selected spans per report. Selection sought maturity/scope contrasts and useful management cases, not random sampling. Excerpts retain exact normalized offsets and PDF physical page or HTML character locators. Whitespace is normalized, soft hyphens and zero-width spaces removed, and HTML scripts/styles/XBRL hidden headers excluded. The 60 exact spans were matched to local parsed source text during curation. PDF extraction and sentence splitting can lose layout or split abbreviations; review cropped one Bank of America span at a complete phrase to avoid the split at U.S. The source register lists retrieval dates, file sizes and parsed page counts. Full issuer documents stay local in data/raw, outside Git.

Sources describe what management reports. An observed statement is not independent verification of the reported outcome. Derived labels, scope, counts and classifier evaluation have status estimated. Fictional staffing/cost/value inputs and their outputs have status scenario.

## Taxonomy

| Label | Review criterion |
| --- | --- |
| deployment | Present operating use, completed rollout or available product capability, with internal versus customer/product scope coded separately. |
| pilot | Explicit experiment, trial, exploration or beta stage. |
| planned | Future intention, commitment or target; no realized result implied. |
| hiring_innovation | People/skills investment, organizational R&D, patents or technical demonstrations without established operating use. |
| promotional | General promise, market opportunity, positioning or broad product description without a specific operational action. |
| risk | Conditional adverse consequence, governance/ethical risk or negative assertion. |
| none | No AI-relevant evidence in the supplied text. |

Labels are single primary categories. Mixed statements retain the primary judgment plus a rationale; this is an acknowledged loss of detail. Internal scope includes the issuer's customer-service operation. Customer/product scope includes vendor offerings and client deployments. Unspecified is retained when the span does not locate the actor clearly. A missing internal-use span means unknown adoption, not zero adoption.

## Classification comparison and review process

The intentionally simple baseline equates an AI term with deployment. The proposed classifier is a deterministic context-rule NLP method, with readable cue precedence and a separate scope heuristic. It has no LLM call or statistical training phase.

A single AI assistant reviewed the actual 60 spans against the rubric, with source-specific reasons in evidence.json. There are no independent human labels, inter-rater agreement, blinded evaluation or held-out test set. Rule development included edge-case corrections; final agreement is descriptive within this selected set. It must not be sold as independently validated accuracy.

The baseline agrees on 23/60 labels; context rules agree on 46/60. Macro F1 averages only review labels present in this sample; the confusion matrix includes all seven taxonomy labels. Fourteen context-rule errors are published with IDs. Scope classification is shown for inspection, but no scope-accuracy claim is made. Reviewed labels drive executive counts; automatic outputs remain separate.

## Workforce and vacancy evidence

Microsoft's functional employment counts are rounded full-time stocks, global consolidated, at June fiscal year-end. Share equals function employment divided by disclosed total, and share change is in percentage points. No skill or occupation crosswalk is applied.

BLS Table 1.2, accessed on 16 November 2026, uses the 2025–2035 vintage. The bundled six rows retain published 2025 baseline estimates, 2035 projected employment, projected growth, annual openings and nominal 2025 wage medians. Rounded values need not sum exactly or reproduce published percentage growth. National projections are not firm vacancies or causal AI forecasts.

Three official employer pages were read for the role matrix. Snapshot date is 16 November 2026; a posting date is not invented when the page does not state one. Their skill tags are assistant coding under corporate-ai-role-tags v1.0. Two employers and three purposively selected roles cannot estimate a market skill distribution or a hiring trend. The vacancy adapter accepts user-supplied permitted CSV/JSON snapshots, validates metadata and duplicates, preserves unknown skill tags as null, and uses only tagged postings as the skill-share denominator. No personal applicant data is required.

## Workforce investment mathematics

For skill k and route r, choose an integer candidate count n. Expected capability by the deadline is n times success probability, if readiness is at or before the deadline. Each skill must meet its own demand. Candidate pools are disjoint across families/routes; no person is counted twice. Capacities are hard candidate limits.

Month-0 cash flow is minus total upfront cost. For months 1 through H, all candidates incur annual recurring cost divided by twelve. Expected successful capabilities earn annual gross contribution divided by twelve only in months strictly after their readiness month. Thus ready_month=4 begins contribution in month 5. Failed candidates still incur modeled cost.

NPV = sum over m=0..H of cash_flow[m] / (1 + annual_discount_rate)^(m/12). PV cost discounts the cost-only flows with the same timing. Payback is the first nonnegative cumulative undiscounted cash-flow month, or null if not reached.

The objective is minimum PV incremental cost subject to per-skill expected coverage, capacity, readiness and an upfront-only cash cap. It does not maximize NPV or impose a total operating-cost budget. Enumeration plus Pareto pruning preserves all undominated upfront/PV-cost combinations; combinations across skills respect the shared cash cap. Benefits can differ slightly across feasible plans because attainment and readiness differ. The minimum-cost objective is retained explicitly.

Existing common payroll is excluded. Training recurring cost is an incremental uplift; redeployment includes backfill/foregone contribution; new hiring includes full incremental loaded payroll. These are scenario definitions. Attainment is an expected yield, not an observed transition probability or guaranteed staffing. Benefits, attrition, taxes, inflation and terminal value must be refit before a real decision.

## Reproduction

From a clone: install the project, then run corporate-ai demo. No network access is needed for the released case. A built wheel contains all data and dashboard assets.

Optional source refresh: install the collect extra, run scripts/collect_reports.py, then scripts/extract_candidates.py. The raw cache prevents repeat downloads. A changed corpus requires a new actual review; do not relabel newly retrieved text as the original review. scripts/curate_evidence.py records the reviewed pinned choices and checks exact offsets. scripts/build_benchmarks.py records the explicitly transcribed official benchmarks; it is not a live statistical API. Full source refresh may encounter issuer/SEC access or rate limits; the offline case remains usable.

No hashes/checksums, BH/FDR or blanket audit battery are part of the workflow. Required checks cover data provenance, arithmetic, input boundaries, packaged installation, cross-runtime agreement and user workflows.
