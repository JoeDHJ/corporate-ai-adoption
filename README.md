# Corporate AI Adoption and Workforce Strategy

**Which AI claims justify a workforce investment—and should a team train, redeploy or recruit?**

[Interactive dashboard](https://joedhj.github.io/corporate-ai-adoption/) · [Executive brief](docs/executive-brief.md) · [Full report](docs/executive-report.md) · [Release downloads](https://github.com/JoeDHJ/corporate-ai-adoption/releases)

A public research case by **Haojian Dui**: ten US-listed firms, twenty official FY2023/FY2024 reports, sixty source-linked evidence spans, official labor benchmarks and a transparent consulting scenario. No paid API, external model or sibling app is required.

![Selected disclosure evidence and modeled workforce choices](docs/figures/decision-evidence.png)

## Inspectable findings

- **Disclosure meaning matters.** Of 60 selected reviewed spans, 23 describe deployment, five pilots, eight plans, eleven people/innovation investments, eight promotional statements and five risks. Customer/product evidence and issuer internal use have separate scopes. Eight company-periods have selected internal-use evidence; the others remain unknown, not non-adopters.
- **Context helps the baseline.** Keyword matching agrees with recorded rubric review on 23/60 spans; context rules agree on 46/60. Fourteen rule errors and all confusion counts are published. Labels came from one AI assistant; no independent human or held-out validation is claimed.
- **Real organizational composition.** Microsoft R&D employment rose from 72,000 to 81,000 in FY2023–FY2024; its global full-time employment share increased by 2.95 percentage points. This is a functional-stock comparison, not an AI-effect estimate.
- **A conditional staffing decision.** A fictional bank unit needing 26 capability equivalents selects 24 training candidates, seven redeployments and one hire: $275,000 upfront and $2.23m PV incremental cost over 36 months. At 50% training attainment, the $400,000 upfront cap cannot meet demand. At $30,000 annual contribution per successful capability, the base plan has negative NPV.

## Run the complete offline case

Python 3.11+; no runtime dependencies.

~~~powershell
python -m pip install .
corporate-ai demo --out output
~~~

Open output/index.html yourself. It is a self-contained file with five modules: decision brief, adoption evidence, workforce signals, strategy lab and methods/sources. It exports filtered CSV, a brief, the changed scenario and portfolio.v1 JSON. The CLI also writes standalone analytical JSON/CSV.

For the wheel downloaded from [Releases](https://github.com/JoeDHJ/corporate-ai-adoption/releases):

~~~powershell
python -m pip install corporate_ai_adoption-1.0.0-py3-none-any.whl
corporate-ai demo --out output
~~~

~~~powershell
corporate-ai classify "Our employees are using AI tools."
corporate-ai scenario --input src/corporate_ai/data/scenario.json --out scenario-results.json
corporate-ai import-vacancies --input examples/official-vacancy-snapshots.csv --out vacancies.json
~~~

The vacancy example contains three actual official employer-page snapshots. It demonstrates the adapter, not a representative vacancy panel or hiring trend.

## Management deliverables

| Deliverable | Purpose |
| --- | --- |
| [Executive brief](docs/executive-brief.md) and [full report](docs/executive-report.md) | Main evidence, quantitative interpretation and limits |
| [Management presentation](docs/management-presentation.md) | Eight-slide decision discussion |
| [90/180/365-day roadmap](docs/roadmap.md) | Proposed owners, evidence and gates |
| [Employer requirements matrix](docs/employer-requirements.md) | Three official JDs mapped to actual outputs |
| [Two-minute demo](docs/demo-script.md) | Repeatable hiring-manager walkthrough |
| [Methods](docs/methodology.md), [data rights](DATA_NOTICE.md), [source register](src/corporate_ai/data/sources.json) | Units, selection, taxonomy, equations, access and rights |
| [portfolio.v1 interface](docs/portfolio-interface.md), [public snapshot](artifacts/portfolio.v1.json) | Standalone reusable data contract |
| [Module screenshots](docs/screenshots) | Original-size UI review evidence |
| [Implementation record](docs/implementation-status.md) | Build, validation, independent review and release |

## Evidence and decision model

Peers: Microsoft, Adobe, IBM, Accenture, Cisco, NVIDIA, Salesforce, Alphabet, JPMorgan Chase and Bank of America. The sample is purposive; fiscal-year ends differ. Every selected span has an exact excerpt, source link, PDF page or normalized HTML offset, retrieval date, rationale and automatic output. Complete parsed report text stays local outside Git.

The optimizer enumerates integer candidate choices and minimizes discounted incremental cost subject to expected coverage by skill, readiness, route capacity and an upfront cash cap. Recurring costs apply to all candidates from month one; contribution starts after readiness for expected successes. NPV discounts monthly flows at an 8% annual effective rate. Common existing payroll is excluded. Internal costs, attainment and value are fictional and exposed; expected capability is not guaranteed headcount.

Six BLS rows share a 2025–2035 projection vintage. Corporate stocks, national projections and selected current JDs have separate windows and denominators. A consistent historical company-vacancy panel is unavailable; the adapter specifies inputs needed for future hiring-response analysis.

## Reproduce and validate

~~~powershell
python -m pip install ".[dev]"
python -m pytest -q
node tests/strategy-parity.cjs
python -m build
~~~

CI runs Windows/Linux and Python 3.11/3.13, including clean built-wheel installation and offline demo. Node is needed for cross-runtime verification only.

Optional official-source refresh:

~~~powershell
python -m pip install ".[collect]"
python scripts/collect_reports.py
python scripts/extract_candidates.py
~~~

The release is pinned. A changed corpus requires a new recorded review; curation does not invent labels for new text. Raw reports are cached in ignored data/raw. BLS/employer snapshots are documented transcriptions with source links. The released outputs regenerate offline. Authored reports regenerate with scripts/build_reports.py; optional static figures use matplotlib.

Original software and authored analysis: MIT. Third-party excerpts retain their rights; see [DATA_NOTICE.md](DATA_NOTICE.md).
