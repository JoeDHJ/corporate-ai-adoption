"""Regenerate professional v2 deliverables from the packaged analytical case."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from corporate_ai.pipeline import analyze
d=analyze();b=d['bank_case'];risk=d['reliability'];w=d['workflow'];half=w['options'][1]
mean=risk['expected_coverage_plan'];robust=next(x for x in risk['allocated_policy_curve'] if x['confidence_target']==.9)
money=lambda x:f'${x:,.0f}'
pct=lambda x:f'{x*100:.1f}%'
def save(name,text):(ROOT/name).write_text(text.strip()+'\n',encoding='utf-8')

save('README.md',f'''
# Corporate AI Adoption and Workforce Strategy

**What should follow an AI rollout: training, mobility, recruitment—or a smaller investment?**

This independently runnable research product connects bank adoption disclosures to task requirements, reliable staffing and an investment decision. Inspect an original statement, change the case, and download the assumptions with the result. Public study by Haojian Dui, developed with AI assistance; no client engagement or independent human-validation claim.

[Live application](https://joedhj.github.io/corporate-ai-adoption/) · [Executive brief](docs/executive-brief.md) · [Full case](docs/executive-report.md) · [Career evidence](docs/career-positioning.md) · [Release](https://github.com/JoeDHJ/corporate-ai-adoption/releases/tag/v2.0.0)

![Workforce decision exhibit](docs/figures/v2-decision.png)

- **Use and risk coexist.** Eleven parsed FY2023–FY2025 reports from four bank groups yield 288 candidate locations and 30 reviewed spans. A Wells Fargo risk paragraph also states current use. Independent axes preserve both. BAC FY2025 remains a visible collection gap.
- **Expected coverage is a weak guarantee.** The original staffing plan has conditional joint attainment of {pct(mean['joint_probability_independent'])}. A 90% allocated policy reaches {pct(robust['joint_probability_independent'])}, increasing personnel PV cost from {money(mean['pv_cost'])} to {money(robust['pv_cost'])}. Success rates are assumptions.
- **Value changes the personnel choice.** The base 50% scale selects 23 training candidates and two redeployments, with {money(half['npv'])} modeled 36-month NPV. Full scale is infeasible under the combined $400,000 cash cap. No action is explicitly compared. Task times and value require actual measurement.

## Run independently

Python 3.11+; no third-party runtime dependencies. Download the release wheel, then:

```text
python -m pip install corporate_ai_adoption-2.0.0-py3-none-any.whl
corporate-ai demo --out output
corporate-ai workflow --out output/workflow-case.json
corporate-ai reliability --out output/reliability-case.json
```

Open output/index.html yourself, or serve output with `python -m http.server --directory output`. output/presentation.html opens directly into the eight-exhibit presentation. Both HTML files embed their public data and work offline. Imported cases stay local. The browser accepts 1–3 distinct skill pools, 30 candidates per route and matched USD 2026 amounts. Edit exported JSON for all task, timing and cost inputs. The CLI accepts `workflow --input case.json`, containing scenario and workflow objects.

```text
python -m pip install ".[dev]"
python -m pytest -q
node tests/strategy-parity.cjs
node tests/v2-parity.cjs
python -m build
```

## Inspect the evidence and methods

| Layer | Delivered proof | Interpretation |
| --- | --- | --- |
| Measurement | Sources, exact locators, 288 candidate locations, independent actor/stage/risk coding | Selected assistant reference judgments; no population adoption rate |
| Text methods | Grouped TF-IDF centroid, keyword/rule baselines, feature-deduplicated temporal check, axis errors | Development diagnostics; no human accuracy claim |
| Hiring | Five readable Citi vacancies and eleven collection outcomes | Targeted external demand; no hiring trend or bank comparison |
| Economics | Workload-derived demand, exact attainment, conservative reliability allocation, joint NPV choice | Conditional scenarios; no causal labor effect or observed savings |
| Research workflow | Six executed document-filtered retrieval tasks and source checks | Fixed assistant-authored task pack, not an unseen/human benchmark |
| Delivery | Offline app, complete presentation, Markdown briefs, schemas, CLI, wheel, CI | Reproducible without a paid model or sibling service |

The original ten-company corpus, Microsoft workforce stocks and BLS projections remain context in their original units. Corporate owns firm evidence and workforce decisions; Atlas, Career Fit and Impact remain optional snapshot consumers.

[Methods](docs/methodology.md) · [Knowledge framework](docs/knowledge-framework.md) · [Interface](docs/portfolio-interface.md) · [Review record](docs/review-log.md) · [Data rights](DATA_NOTICE.md)
''')

save('docs/executive-brief.md',f'''
# An AI rollout needs a workforce decision
Haojian Dui · 16 November 2026 · v2.0.0 · Public evidence and explicit scenarios

Bank disclosures identify operating use cases. A workforce investment additionally requires task requirements, eligible people, a reliability constraint and an incremental-value mechanism.

Eleven complete annual reports cover JPMorgan Chase, Bank of America, Citi and Wells Fargo across FY2023–FY2025, with BAC FY2025 missing after collection failure. Thirty reviewed spans sit inside 288 candidate locations. JPMorgan FY2024 LLM Suite rollout reach and FY2025 CIB active users describe different populations; they cannot establish a decline. Wells Fargo's repeated use-plus-risk disclosure is not a new annual deployment event.

The original fixed-demand staffing mix meets expected requirements but has only **{pct(mean['joint_probability_independent'])} joint attainment** under additional independent Bernoulli assumptions. A conservative 90% allocated policy yields **{pct(robust['joint_probability_independent'])}**, at **{money(robust['pv_cost'])}** personnel PV cost versus **{money(mean['pv_cost'])}**. These probabilities are conditional calculations, not measured employee success rates.

The completed workflow case derives separate skill demands from task minutes, reserves integration cash, and jointly compares cost, readiness and reliability. Of no action and 25%, 50%, 100% scale, **50%** wins under base assumptions: **23 training candidates and two redeployments**, **{money(half['npv'])} modeled NPV**, and **{pct(half['break_even_realization'])} selected-plan break-even realization**. Full scale is cash-constrained. At zero realized value, no action wins. A changed value can change the optimal mix, so the selected-plan threshold is not a global switching threshold.

Use an actual analyst pilot to measure task/revision time, source correctness, attainment and capacity monetization before investment. Six executed software tasks do not measure human productivity. Five readable Citi vacancies establish selected role requirements, not hiring growth.

[Interactive case](https://joedhj.github.io/corporate-ai-adoption/) · [Full report](executive-report.md) · [Methods](methodology.md)
''')

table='\n'.join(f"| {pct(x['scale'])} | "+(f"{money(x['upfront_with_integration'])} | {money(x['pv_total_cost'])} | {money(x['npv'])} | {pct(x['staffing']['joint_probability_independent'])} |" if x['staffing']['feasible'] else 'Infeasible | — | — | — |') for x in w['options'])
save('docs/executive-report.md',f'''
# Corporate AI Adoption and Workforce Strategy
Haojian Dui · 16 November 2026 · Version 2.0.0

## The operating question

Which AI claims establish use, and what workforce investment should follow? The study makes the transition explicit: disclosure → workflow → task time → skill demand → reliable staffing → realized value. The applied workflow is public-document research and evidence checking, motivated by bank coding, research and document-processing uses. Public information establishes relevance; internal task times, candidate pools and operating return remain assumptions.

## Bank evidence and measurement

Four large US-listed bank groups are followed across three December year ends. Eleven full official annual reports were parsed. BAC FY2025 could not be downloaded completely from SEC; its issuer CDN returned 403. That cell is a collection failure. A Goldman Sachs expansion also failed at its official CDN and was excluded from this release cohort, not assigned a negative outcome. The cohort is purposive and access-conditional.

All parsed pages are searched for the bank lexicon. Eligible 8–80-word punctuation spans yield 288 candidate locations; PDF layout, hyphenation, implicit tool references and sentence limits can miss context. This is full parsed-text scanning, not exhaustive human adoption review. Thirty selected spans have exact locators and assistant reference judgments. The earlier ten-company corpus remains a separate technology comparison.

Actor and stage are separate from technology, people investment and risk. Wells Fargo states current use and warns about uncertain outcomes in one paragraph. Its FY2023/FY2024 repetition is not a second event. Citi FY2023 reviewed risk language leaves internal adoption unknown. Fiscal period and event time differ; exact event dates remain null where the span does not establish them. Rollout reach, active users, interactions and reported capacity hours retain different denominators and are not combined into an intensity score.

The binary text diagnostic contains 82 selected assistant-reference rows including financial negatives. TF-IDF vocabulary, IDF and class centroids are fitted outside each held-out company. Rules retain development exposure. The temporal check excludes one feature-identical financial sentence whose numbers changed, leaving six FY2025 rows. Actor, stage and risk errors are separately published. Technology, people and numeric fields are rule-derived. None of these results establishes independent human accuracy.

## Hiring and task requirements

Five readable Citi vacancy snapshots, from eleven attempted Citi/JPMorgan pages, request combinations of Python, production delivery, integration, evaluation, retrieval and governance. Collection outcomes distinguish fetch failure from JavaScript-only pages. Four primary-location advertised salary ranges are retained; one missing parsed range remains null. The targeted AI-role sample cannot establish skill prevalence, hiring trends or employer differences. Senior role qualifications exceed what this project demonstrates.

The fictional research unit processes 60,000 document items monthly at full scale. Specialist task minutes are 0.8 for evaluation, 1.2 for integration and 0.6 for data exceptions. At 100 productive hours per person-month, the distinct requirements are 8, 12 and 6 FTE. Assisted execution is eight minutes and expected rework 0.8 minutes, against a 20-minute baseline. These are planning assumptions awaiting observation. Disjoint candidate pools prevent counting the same person as several successful skill assignments.

## Reliability and investment

The original expected-coverage plan has {pct(mean['joint_probability_independent'])} conditional joint attainment. Exact Bernoulli distributions yield skill probabilities and expected shortfall. Equal failure-budget allocation provides a sufficient joint constraint. The 90% policy has a {pct(robust['joint_probability_lower_bound'])} union lower bound and {pct(robust['joint_probability_independent'])} independent product probability. Candidate independence within each skill is assumed; cross-skill independence is additionally required for the product. The allocated policy is conservative, not the unrestricted globally optimal joint chance constraint.

At each scale, the workflow optimizer reserves integration cash and jointly compares personnel PV cost, slowest readiness and joint probability. It enumerates eligible integer mixes and applies sufficient Pareto dominance before checking shared-budget combinations. A more expensive early or reliable route can beat the cheapest staffing mix. Value is counted once per workflow, conditional on all skill demands being met, after the latest route and permitted launch. Redundant candidates do not create additional capability-level benefits.

| Scale | Upfront incl. integration | Total PV cost | Workflow NPV | Conditional joint attainment |
| --- | ---: | ---: | ---: | ---: |
{table}

Amounts use constant USD 2026 assumptions over 36 months and an 8% annual discount rate with monthly timing. Recurring staffing costs start in month one for all candidates, including failures. Platform costs also start in month one. Training includes learning time; redeployment includes backfill/opportunity cost; hires include fully loaded compensation. Existing base payroll is common to alternatives. Integration scales proportionally here. The 50% plan uses 23 training candidates and two redeployments and breaks even at {pct(half['break_even_realization'])} realization for its selected mix. Reoptimization can change that mix.

Released hours are productive capacity. Value/hour and realization convert that capacity to incremental contribution or avoided cost under an assumed mechanism. They are not observed wages or cash savings. Do not add revenue from the same hours a second time. No action has zero incremental NPV. The policy comparison covers four discrete scale choices, not every possible scale. Attrition, taxes, inflation, partial value under skill shortfall and salvage value remain omitted assumptions.

## Delivery and actual evidence still needed

The app provides original-source links, a bank-period matrix, executable task presets, locally editable inputs, JSON import/export, and a matching Markdown brief. The eight-exhibit presentation supports a business discussion without a coding walkthrough. The wheel includes data, schemas and web assets and has no runtime service or paid-model dependency. Python/browser parity and independent small enumerations check the calculations.

The six fixed retrieval tasks match assistant-authored references and exact source locators. They search only the released excerpts after document filtering. They are functional task checks, not unseen retrieval validation or employee productivity estimates. A real analyst crossover pilot needs actual consented participation, independent quality review and observed task/revision times. Finance must verify how released capacity is monetized before calibration can support a real investment.

[Knowledge framework](knowledge-framework.md) · [Career evidence](career-positioning.md) · [Decision gates](roadmap.md) · [Review record](review-log.md)
''')

save('docs/methodology.md','''
# Methods and equations — v2

The frozen public snapshots reproduce the app offline. Collection is separate and may fail when issuer sites change. Complete parsed reports remain in ignored data/raw. Source identity, paths, byte sizes, timestamps and physical-page/character locators track provenance; no explicit hashes are used.

The bank lexicon includes AI, artificial intelligence, machine learning, generative AI, Copilot, LLM Suite, Citi tools, Erica and Fargo. Issuer names Bank of America and Wells Fargo alone are not hits. Candidate locations represent eligible punctuation spans, not adoption intensity. Reviewed actors/stages/risk are assistant judgments; other axes are rule-derived. The binary deployment target includes customer products, unlike internal-use evidence in the matrix. Repeated text does not establish a new event.

TF-IDF cosine nearest-class centroids fit vocabulary, IDF and centroids on training data only, without parameter search. Company groups are held out together. Temporal checks fit FY2023/FY2024 and remove test rows with token-count features identical to training. Rules were developed against part of the material. Published confusion counts, axis disagreements and the six-row future-language sample are development diagnostics, not independent human validation.

For each skill j, candidate counts n_jr on routes r have independent Bernoulli probabilities p_jr. Routes ready after the deadline contribute zero. Convolution gives P_j(k). Attainment is sum over k >= demand_j; expected shortfall is sum max(0,demand_j-k)P_j(k).

For target q across J skills, equal allocation requires every skill's probability >= 1-(1-q)/J. The union bound then ensures joint probability >= q without cross-skill independence. The displayed product additionally assumes independence across skills. Constant success and within-skill independence remain assumptions. The common-shock calculation is a stress, not a calibrated correlation estimate.

The reliability curve minimizes personnel PV cost in each allocated policy. It is not a global efficient frontier. The workflow solver maximizes workflow NPV within that same policy class by comparing cost, probability and latest readiness. Pareto pruning uses upfront/PV cost, launch time and probability. Independent tiny exhaustive enumerations test the optimum. Scale choices are 0%, 25%, 50% and 100%.

Demand_j = ceil(scaled monthly volume × specialist minutes_j / 60 / productive hours per person-month). A relative 1e-12 arithmetic tolerance avoids adding a worker when a mathematical integer becomes 2.0000000000000004. Separate disjoint skill demands are capped at 100 each. The browser permits three skill pools and 30 candidates per route.

Human time after adoption = assisted execution + specialist task minutes + rework probability × rework minutes. Released hours = scaled volume × (baseline minutes - after minutes) / 60. Expected monthly value = released hours × value/hour × realization × joint attainment probability. The all-or-nothing assumption assigns no workflow contribution when any skill requirement fails. Value begins strictly after permitted launch and slowest selected readiness. Recurring staffing/platform costs start in month one; upfront spend is at month zero. Discount factors use (1+annual rate)^(month/12). Integration is reserved in the cash cap and counted once.

Workflow NPV does not use the legacy annual_value_per_capability field; that field remains for the original fixed-demand comparison. Legacy per-capability benefit fields are removed from workflow staffing exports. Currency/price year must match; browser cases use USD 2026. The selected-plan realization threshold holds staffing fixed and is not a global switching threshold.

Install the wheel and use corporate-ai demo, workflow or reliability. Pass an exported case through workflow --input. scripts/collect_banks.py collects original public reports; scripts/build_bank_case.py rebuilds the pinned assistant references from local texts. Review indexes after parser/source changes. scripts/benchmark_research.py reruns the fixed task pack when local originals exist. scripts/build_reports.py and scripts/build_v2_figures.py regenerate professional outputs. A frozen installation needs no originals or network.
''')

save('docs/knowledge-framework.md','''
# Economic knowledge made operational

| Idea | Implementation | Evidence needed to replace assumptions |
| --- | --- | --- |
| Task substitution and new tasks | Count execution, evaluation, integration, exceptions and rework separately | Observed task/revision minutes at equal quality |
| Complementary intangible investment | Integration, learning time and platform costs precede contribution | Actual cost, ramp and skill-transfer observations |
| Human capital and mobility | Distinct pools, eligible capacity, success and backfill costs | Skill assessment, attainment, attrition and backfill |
| Stocks and flows | Employee functions, vacancy snapshots and national projections remain separate | Comparable source populations and genuine longitudinal observations |
| Measurement error | Independent axes, unknown states and disclosed coding failures | Independent human references and larger future cases |
| Uncertain decisions | Exact probability, shortfall, allocated reliability and no action | Failure consequences and correlated-success evidence |
| Opportunity cost | Realization is needed to monetize released capacity | Finance-verified avoided hiring, backlog conversion or service contribution |

Acemoglu and Restrepo's task framework explains why automation can displace tasks while new tasks change labor demand. It motivates task accounting here; it does not supply this case's coefficients or a bank headcount forecast. [Automation and New Tasks, NBER w25684](https://www.nber.org/papers/w25684).

Brynjolfsson, Rock and Syverson describe complementary investment in the productivity J-curve. This motivates separating early integration/learning costs from delayed contribution; the case does not estimate a J-curve. [The Productivity J-Curve, NBER w25148](https://www.nber.org/papers/w25148).

Selection prevents causal interpretation: banks adopting AI also change processes, technology, strategy and staffing. Disclosure comparisons cannot isolate an AI employment effect. A prospective analyst task experiment can identify effects on defined tasks under its assignment and measurement conditions; it cannot alone identify firmwide employment effects. Actual participants, independent quality review and task-time observations are required. The included protocol prepares that work without inventing records.
''')

save('docs/career-positioning.md','''
# What this project demonstrates in hiring

Position this as evidence-led AI workforce strategy with reproducible analysis. Its strongest role families are applied research/economics, workforce analytics, AI strategy and analytical product work. Senior job descriptions reveal relevant requirements; the project does not substitute for senior experience.

| Dimension | Concrete proof | Interview demonstration | Boundary |
| --- | --- | --- | --- |
| Ability to frame a problem | Disclosure → tasks → staffing risk → investment | Explain why rollout reach cannot determine a training budget | No internal client discovery |
| Knowledge depth | Task accounting, opportunity cost, complementarity and uncertainty | Explain why capacity is not cash and expected coverage is not guaranteed | Parameters remain assumptions |
| Analytical skill | Exact probability, integer choice, joint NPV, grouped TF-IDF and visible errors | Show an earlier costly hire beating the cheapest plan | No causal employment estimate or independent labels |
| Engineering | Packaged data/schemas, CLI, offline app, parity, CI and clean installation | Import a case and reproduce the decision from a wheel | No enterprise service operations history |
| Experience | Matrix, task presets, missing states, stale-export protection, matching brief | Move from source to a changed-input decision | No actual external usability participants |
| Presentation | Two analytical figures, eight rendered exhibits, short/full reports | 30-second result, three-minute case, deeper source/method follow-up | Visual clarity does not validate assumptions |

Project description, only if the author can explain and defend the work: “Developed a reproducible banking AI evidence and workforce investment study, combining source-level adoption measurement, grouped text diagnostics, exact staffing reliability and workload-based NPV scenarios in an offline decision application.” Attribute AI assistance accurately. Do not present modeled NPV as money saved for a client.

For economics roles, lead with measurement and identification. For workforce analytics, lead with task demand, readiness and mobility cost. For AI strategy, lead with the operating question and threshold. For analytical engineering, lead with data contracts, reproducibility, error handling and parity. Each route should include an original-source check and a live changed-input calculation.

Real analyst participation, independent coding and measured quality/value outcomes would add evidence beyond what software alone can provide. The task pack, protocol and adapters prepare those steps; simulated logs would not establish them.
''')

save('docs/management-presentation.md',f'''
# Eight-exhibit presentation — v2

Use the app's Presentation tab or generated presentation.html. Each is a complete rendered view.

1. Which operating evidence warrants workforce investment?
2. Preserve actor, stage and use-plus-risk meaning.
3. Eleven bank reports, 30 reviewed spans, 288 candidate locations; gaps visible.
4. Mean-coverage joint attainment {pct(mean['joint_probability_independent'])}; allocated 90% policy {pct(robust['joint_probability_independent'])}.
5. No action and three scales; base 50% NPV {money(half['npv'])}; full scale cash-constrained.
6. Selected-plan realization threshold {pct(half['break_even_realization'])}; recompute when assumptions change.
7. Process, learning, controls and finance owners verify measured gates.
8. Source measurement, methods, complete app and independent reproduction.

Figures are reusable with their scenario notes. No observed savings or client engagement is claimed.
''')

save('docs/demo-script.md','''
# Three-minute demonstration — v2

1. Open Decision brief. Explain conditional shortfall and scale selection; name the scenario assumptions.
2. Open Bank evidence. Click WFC FY2024 to inspect use plus risk. Choose citi-2025-coding in the task menu and check the source. Distinguish capacity from cash.
3. Open Workflow decision. Show workload-derived demand. Set realization to zero, recalculate and show no action. Reset. Increase the cash cap to $700,000 and inspect the newly feasible full-scale alternative and its route mix.
4. Export the changed case and matching Markdown brief. Import the JSON back and verify the decision. Inputs stay local.
5. Open Methods. Inspect axis failures and the small feature-deduplicated time check; disclose assistant reference labels.
6. Open the eight-exhibit Presentation. End with wheel installation and the actual pilot evidence needed before real investment.
''')

save('docs/roadmap.md','''
# Decision gates with accountable evidence

| Gate | Owner | Required evidence | Decision |
| --- | --- | --- | --- |
| First 30 days | Process/analyst lead | Actual baseline time, quality, exceptions and data access | Confirm volume and specialist task minutes |
| Days 30–60 | Learning/workforce | Assessed eligible pools, actual attainment and transfer | Replace capacity/success assumptions |
| Days 60–90 | Controls | Independent source quality and failure severity | Permit or stop workflow use |
| Day 90 | Finance/process | Actual integration/platform costs and capacity monetization | Recompute scale and no action |
| Day 180 | Workforce/finance | Attrition, correlated failure, sustained quality/value | Scale, redesign or defer |
| Day 365 | Executive owner | Comparable outcomes and refreshed labor signals | Renew business case and ownership |

The software, public case and decision flow are delivered. Independent human coding, actual analyst experiments and client outcomes require real participation; synthetic records cannot complete them. A disclosure-count regression would not resolve these gaps.
''')

save('docs/implementation-status.md','''
# Implementation status — v2.0.0

Delivered: preserved v1; bank cohort through FY2025 with eleven parsed reports and one missing cell; 288 locations; 30 multi-axis references; grouped TF-IDF and feature-deduplicated temporal checks; axis errors; five real Citi snapshots and eleven collection outcomes; exact conditional attainment/shortfall; conservative reliability; workload demand and joint NPV personnel choice; no action/three scales; case import/export and matching brief; task presets; eight presentation views; professional reports and reproducible package.

Boundaries: assistant labels, no human-study participants, no causal employment effect, no observed client return, no representative vacancy sample. BAC FY2025 and Goldman Sachs report collection encountered download failures/403; JPMorgan vacancies required rendering and one Citi vacancy failed. Coverage outcomes remain explicit. Full original text stays local; only short excerpts enter the public package.

See review-log.md and release-record.md for actual validation and publication. Changed/failed paths receive targeted rechecks; unchanged passed checks do not trigger repeated broad audits.
''')
print('Regenerated v2 README and 10 professional reports.')
