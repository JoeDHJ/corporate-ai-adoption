# Independent review and closure
16 November 2026 · Release 1.0.0

Two independent read-only reviewers examined requirements, logic, edge cases, code quality, test coverage and actual runtime. They did not modify files or use browser automation. The primary agent completed UI verification separately.

| Finding | Resolution and regression evidence |
| --- | --- |
| Integer-valued floats passed validation but failed integer enumeration | Reject them consistently before solving; explicit boundary checks. |
| A binding upfront cash cap was reported as insufficient candidate capacity | Track capacity-feasible options separately in Python and browser solvers; zero-budget and cross-runtime checks. |
| Equal skill strings from different taxonomies/versions could be merged | Reject mixed coding systems before skill-share aggregation. |
| Explicit zero tags were turned into missing tags | Preserve [] versus null; check the tagged-observation denominator. Validate taxonomy/version strings. |
| Evidence rows could override authoritative source metadata | Source registry fields take precedence; injected URL/company/period regression. |
| Formal schemas were missing | Four bundled JSON Schemas plus CLI schema output; validate actual generated and saved artifacts. |
| Standalone scenario/sensitivity exports omitted inputs and provenance | Wrap complete inputs/results with portfolio metadata; changed-budget contract checks. |
| Jobs lacked canonical company and coding metadata | Add SEC-CIK, native job identity and estimated skill-coding status. |

Both reviewers rechecked the affected paths and closed all findings. They reported no remaining P0/P1/P2 or material requirement gap. One independently matched all sixty selected spans to twenty local parsed reports and verified report identity/vintages. The default scenario remained 24/7/1, $275,000 upfront, $2,229,643 PV cost and $9,142,257 NPV.

Final local validation: 37 Python checks; browser/Python parity for five scenarios and four route policies; filtered CSV serialization and spreadsheet-cell safety; built-wheel installation and offline data/dashboard generation in a clean environment. Browser checks cover filters, empty results, source links, scenario recalculation, 50% attainment infeasibility, negative NPV, missing input, stale-export protection and all four export-preparation actions, with no console errors.

Seven complete original-size screenshots cover all five desktop modules and the mobile brief/strategy views. Mobile layouts were checked at 390 CSS pixels for page overflow. Desktop captures use 1440 pixels. Screenshots are saved under docs/screenshots.

The browser automation's download-completion event did not expose a saved-file path, and the browser security policy blocked its internal downloads-history page. No bypass was attempted. UI preparation and payload serialization were verified; on-disk exports were independently verified through the CLI. This is a verification-tool limit, not a missing product export.

## v2 — substantive review and optimization, 16 November 2026

Two independent read-only reviewers examined evidence, methods and mathematical decisions. Round 1 verified all 30 new source locators, report years, 288 candidate bounds, five real vacancy records, exact Bernoulli probabilities and small constrained choices. Round 2 corrected and targeted-retested the issues below. The reviewers closed their findings with no remaining P0/P1 or material P2 in their reviewed scope.

| Finding | Completed correction |
| --- | --- |
| A WFC span was described as agentic although it only states Copilot deployment | Corrected the reference reason; no stronger maturity claim |
| JPM FY2025 inherited a FY2023 native ID | Restored source-native year identity |
| Changed numbers hid feature-identical temporal text | Excluded the one duplicate feature row; six future-language rows remain |
| New axes lacked corresponding evaluation | Published actors 21/30, stages 21/30, risk 27/30 exact agreement and every error; other axes explicitly rule-derived |
| UI phrase search could not reproduce task-pack ranking | Shared count/rank semantics and six executable task presets; complete ranking parity checked |
| Cheapest reliable staffing could falsely imply no investment is worthwhile | Jointly optimized personnel PV cost, readiness and probability within the allocated policy class; independent one-/two-skill counterexamples pass |
| Zero hourly value divided by zero | Null threshold; no action and finite cost/NPV still computed |
| Different currencies/price years could be combined | Reject mismatches; browser cases use USD 2026; validate dates |
| Floating point ceil could add a worker at an integer boundary | Shared arithmetic tolerance; 3000 × .28 / 60 / 7 gives 2 |
| Workflow exports could contain legacy per-capability benefit fields | Remove them from both positive-value and fallback staffing outputs; Python and browser checks |

Round 3 covers employer-facing clarity, user experience and visual presentation: complete decision chain and career evidence matrix; source-to-task presets; base, no-value and relaxed-budget decisions; stale-export protection; matching export preparation; eight rendered presentation exhibits; original-size desktop/mobile captures. The first figure inspection found clipped labels and overlapping notes; margins were corrected and the regenerated figure inspected at native size.

The browser extension did not permit file access for automated upload, so native file-chooser completion could not be certified. No extension permission was changed. Actual JSON files and the shared import validation/solver were checked through the CLI and Node; the UI upload control and error boundary remain implemented. Export preparation is visible; saved-browser-download paths are not claimed. No real usability participants or human productivity observations were invented.

V2 validation: 53 Python checks before the additional provenance regression (54 checks in the release suite); five new Python/browser workload/value/reliability parity cases and five legacy scenarios × four policies; six task rankings match across Python/browser. Desktop screenshots use 1440 CSS pixels and mobile screenshots 390; all three mobile modules have scrollWidth=390 with no page overflow. Base, zero-realization and $700,000-budget UI decisions and stale-export protection were exercised with no console errors. Six desktop modules and three mobile modules have complete original-size captures.

A wheel installed with --no-deps in a new isolated environment generated both standalone HTML views, loaded all bank data, and reproduced the imported JSON case and $1,907,704 half-scale NPV. The isolated import resolved to that environment’s site-packages.
