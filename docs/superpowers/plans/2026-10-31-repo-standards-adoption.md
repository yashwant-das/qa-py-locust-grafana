# Repo Standards Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task, inline in one session. Preserve the existing project's preference against subagents unless the owner requests them. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply repo-standards to this flagship load-testing repository without losing accurate documentation, technical detail, executable behavior or landing-page impact.

**Architecture:** Preserve the five-service Docker Compose design and functional directories. Extend the existing showcase README with two maintained guides and pinned agent guidance; introduce reproducible Python dependencies, staged checks and hardened CI around the existing load-test pipeline.

**Tech Stack:** Python 3.13, Locust with built-in OTLP export, Flask/gunicorn, prometheus-client, Prometheus, Grafana, Docker Compose v2, pytest, uv, Ruff, mypy, pre-commit and markdownlint-cli2.

**Spec:** The owner's 2026-10-31 request is the controlling requirement: the existing README and docs are accurate; preserve their data and flagship impact. The design and preservation contract below make that requirement concrete. Policy source: [repo-standards at a429dd2f2da55a4c3e1c73c7c0d1111f9cd0b9a9](https://github.com/yashwant-das/repo-standards/tree/a429dd2f2da55a4c3e1c73c7c0d1111f9cd0b9a9), including its README, AGENTS and all five guides.

## Global constraints

- Planning only in this change. Implementation, installs, dependency resolution, Docker runs, publication and settings changes are later work.
- Use the `complete` profile. Record the full standards SHA in `AGENTS.md` and detailed evidence in `docs/development.md`; keep rollout metadata out of the root README.
- The local audit base is clean `main`, commit `a7580551727e14352542f6208c109cb9aee595e9`; no remote freshness is claimed. Reconcile the fetched default branch before implementation and review any differences before using this plan.
- Existing README and docs are authoritative. Make additions and narrowly justified command/tooling updates, not a blanket rewrite or generic template replacement.
- Preserve Python 3.13. Retain the established 120-character Python line-length convention from the existing design record. Changing the runtime baseline needs owner approval.
- Preserve `locustfiles/`, `target-app/`, `grafana/`, `tests/` and `docker-compose.yml`. No forced `src/` layout, new packaging layer, exporter, database, Alertmanager or tracing service.
- Preserve one gunicorn process, eight threads and five-second keep-alive; 20-user autostart; localhost-only published ports 3000, 5001, 8089 and 9090; anonymous Grafana Viewer access; existing datasource/dashboard UIDs and 11 panels.
- Preserve CLI flags, expected negative-response handling, request names, task weights, latency simulation, seeded users and capped storage. Formatting and typing must not alter behavior.
- Keep the screenshot at `docs/dashboard.png` unchanged. The standards permit existing docs image locations until migration; moving it is unnecessary for this adoption.
- Preserve the entire historical [simplification plan](2026-10-12-simplify-load-test-stack.md) unchanged, including code, observations, commands and rationale. Label its historical role from the documentation index; do not execute its old rewrite/delete instructions.
- Do not turn historical timing observations into guaranteed benchmarks or newly verified evidence. Every verification record states revision, date, environment, command, result and skipped scope.
- Preserve MIT licensing. No unrelated sibling changes, merges, remote settings changes or silent standards repinning.

## Design and approach

Use a preservation-first, incremental adoption. The README already supplies badges, the spike visual, a concrete value proposition, an inline architecture diagram, a working quickstart, scenarios, alerts, results and stack/layout summaries. Retain them and add navigation, explicit capabilities and clear offline verification. Add the missing guides rather than hollowing out the landing page.

A template-driven rewrite would risk losing accurate explanations and visibility. A documentation-only adoption would leave dependencies and quality gates incomplete. This plan covers full adoption in independently reviewable tasks, with documentation preservation checked before and after tooling work. These are proposed implementation choices, not a claim of owner approval to execute them.

Use a root non-packaged uv project for the multi-service test repository. Keep the target app's standalone Docker build context by exporting its runtime requirements from the root lock. Keep both existing requirements entry points as generated compatibility files, not independent dependency authorities. Review compatible stable package updates during execution; do not guess new versions in this plan.

## Current audit

| Area | Observed state | Planned treatment |
| --- | --- | --- |
| Landing page | Complete showcase story, six badges, screenshot, Mermaid, quickstart, scenarios, results, alerts, stack and tree | Preserve; add missing navigation and focused verification/capability details |
| Existing docs | Dashboard PNG and 1,503-line historical implementation plan | Preserve both; extract current operational knowledge into new guides with historical attribution |
| Required guides | No `AGENTS.md`, `docs/architecture.md` or `docs/development.md` | Add useful repo-specific content |
| Python configuration | Python 3.13 in CI/container; `pytest.ini`; direct pinned requirements | Add runtime declarations, non-packaged `pyproject.toml`, uv lock and generated requirements |
| Existing direct versions | Locust 2.46.7, pytest 9.1.1, Flask 3.1.3, gunicorn 26.2.0, prometheus-client 0.26.0 | Audit at execution; retain until a compatible update is demonstrated |
| Containers | Locust OTEL 2.46.7, Prometheus 3.15.0, Grafana 13.2.3, Python 3.13-slim | Preserve compatibility set and saturation story during version review |
| Tests | API/metrics tests and threshold tests; historical record states 24 passing cases | Measure fresh baseline; historical count is not a new test result |
| CI | Existing full-stack wiring and 60-second gated load test, summary and HTML/CSV artifact | Retain pipeline and identity; add separate offline quality job |
| CI safety | `contents: read`, PR trigger and 15-minute timeout already present; action tags, default checkout credentials, 30-day artifacts | Keep existing safeguards; add full SHA pins, disabled credential persistence, lock cache and three-day artifacts |
| Local gates/updates | No tracked Ruff/type/Markdown/pre-commit configuration or Dependabot file | Add aligned offline gates and weekly dependency/action updates |
| Remote metadata/security | Not inspected during local planning | Read during execution; prepare proposals without changing settings |

## Documentation preservation map

This map is the minimum acceptance checklist. At implementation start, inventory every paragraph, list, table row, command, link, image and diagram edge against the exact fetched base. Record any relocation in `docs/development.md`; a summary cannot replace unique source detail.

| Existing source | Must remain visible in README | New guide coverage |
| --- | --- | --- |
| Title, summary and badges | Distributed load, bundled Flask target, shared client/server dashboard, all current badge meanings and working CI link | Explain supported runtimes/tooling separately |
| `docs/dashboard.png` and alt text | Full existing spike visual immediately near opening; client latency versus handler-time contrast | Link to original image; retain historical provenance |
| Why it exists | Queueing explanation, 200 users, about one-second client p95, about 240 ms app p95 and eight-thread cause | Explain measurement boundaries and environment-dependent results |
| Architecture diagram and paragraph | Master/workers, HTTP load, worker request OTLP, master user-count OTLP, app scrape and Grafana query edges | Detailed startup, request/metrics lifecycle and trust/network boundaries |
| Quickstart and service table | Clone/start command, automatic 20-user load, no setup/login, all service URLs and notes, admin editing credentials | Runtime/tool prerequisites, clean setup and troubleshooting |
| Ports and worker controls | Localhost bindings, four-worker scaling command and shutdown command | Internal versus published ports, scaling checks and cleanup |
| Scenarios | Both paths, expected 404/400, repeating 50/200/10 shape for 120/60/120 seconds, `LOCUSTFILE` command and latency-alert narrative | Add/change scenarios, shared class discovery, task weights, wait time and explicit stop instructions |
| Test reports and results | Existing three CI stages, 60 seconds/20 users, 500 ms and 1% limits, workflow link, summary, HTML/CSV and `locust-report` | Full quality commands, threshold semantics, artifact retrieval and execution scope |
| Local gate command | Runnable equivalent with same Locust flags, host and report capability after uv migration | Canonical setup and full report commands; preserve compatibility pip path |
| Dashboard and alerts | Dashboard title, displayed metrics/breakdowns, all three alert names/thresholds/15-second durations, alerts URL and no notifications | Query semantics, units, evaluation windows and validation commands |
| Tech stack and structure | Every existing layer/tool/purpose and functional directory; truthful versions after any verified update | Link authoritative manifests and explain additional tooling files |
| License | Existing MIT wording and link, last section | No licensing change |
| Historical plan: design summary and Tasks 1–2 | Keep the concise landing-page story | Metric source/label table; client histogram caveat; five request names; 6/3/2/1/1 weights; 1–3 second waits; seeds 1–5; cap 1,000; expected negatives; validation and threshold boundaries |
| Historical plan: Tasks 3–4 | Retain screenshot, alerts and architecture | Mount-hiding bug rationale, disabled plugin installer, OTLP naming, worker `instance` separation, datasource health, all panel purposes, promtool and alert verification |
| Historical plan: Tasks 5–6 | Retain report/CI story and usable first-run commands | Wiring probes, summary/report paths, screenshot reproduction conditions and dated observations; keep obsolete branch/deletion instructions only in history |

## Review focus

1. Documentation loss despite passing lint: reconcile the preservation map and inspect the rendered README, Mermaid and screenshot in Tasks 1 and 5.
2. Dependency changes that flatten the headline latency gap: repeat the steady and spike runs with the same worker/thread configuration in Tasks 2 and 5.
3. Misleading metrics despite nonempty series: verify correct histogram units, expected-negative failure handling and separate worker identities in Tasks 4 and 5.
4. Gates that pass without exercising behavior: retain zero-request failure and threshold exit-code tests; probe a deliberately failing CLI run in Task 5.
5. Hooks or CI that miss relevant files or alter unstaged edits: test staged-file filtering, partial staging and independent full-file checks in Tasks 3 and 4.

## File change boundaries

| Files | Planned responsibility |
| --- | --- |
| `README.md` | Focused additive showcase, links and updated verified setup/quality commands |
| `AGENTS.md` | Pin/profile, guide routing, preservation and runtime rules, agent trust and hook rules |
| `docs/architecture.md` | Current architecture, lifecycles, metric contracts, boundaries and trade-offs |
| `docs/development.md` | Current setup/configuration, extension workflow, quality commands, evidence and exceptions |
| `pyproject.toml`, `uv.lock`, `.python-version` | Python metadata, default app dependencies, dependency groups and locked quality tooling |
| `requirements-dev.txt`, `target-app/requirements.txt` | Generated, hash-bearing requirements exports preserving existing install paths |
| `target-app/Dockerfile` | Consume the generated locked runtime requirements; preserve runtime and gunicorn behavior |
| `.pre-commit-config.yaml`, `.markdownlint-cli2.jsonc`, `.gitignore` | Staged checks, Markdown baseline and tool-output exclusions |
| `.github/workflows/load-test.yml` | Existing load pipeline, hardened and extended with offline quality gates |
| `.github/dependabot.yml` | Weekly Python and action updates; supported image coverage after checking updater capabilities |
| `target-app/app.py`, `locustfiles/*.py`, `tests/*.py` | Only required typing/import/format adjustments; behavioral changes require separate justification |
| `docker-compose.yml`, `grafana/**` | Preserve service/query behavior; change only for verified compatible updates or focused verification fixtures |
| `tests/prometheus-alerts.yml` | New promtool behavioral fixtures for alert rules |
| `pytest.ini` | Retain test paths/import discovery; do not duplicate or migrate without a concrete need |
| Existing PNG and historical plan | No edits, moves, replacements or deletions |

## Task 1: Establish baseline and add documentation without loss

**Interfaces:** Consume the fetched default branch and pinned policy; produce the preservation record and three missing guidance files. No dependency or application changes.

- [ ] Fetch target origin and compare its default branch with the audit base. Preserve unrelated work and existing branches; create `codex/adopt-repo-standards` from the fetched default branch. Carry this planning file into the working branch safely.
- [ ] Save baseline content hashes for the PNG and historical plan and inventory all tracked documentation. Record baseline direct versions, service configuration and fresh unit-test result using the existing environment if usable; otherwise mark the baseline run unavailable with its cause.
- [ ] Complete the paragraph/table/command preservation inventory from the map above. Keep all existing showcase content on the landing page; add 3–6 concrete capabilities, guide links and an offline-versus-stack verification distinction. Group stack/tree material with architecture if it improves scanning; preserve its contents.
- [ ] Create `AGENTS.md` with profile `complete`, the full pinned policy URL/SHA, relevant guide routing, preserved project conventions, untrusted-content/secret boundaries and prohibition on bypassing failed hooks. Do not import historical operational instructions as current rules.
- [ ] Create `docs/architecture.md`: five service responsibilities; request and metric lifecycle diagrams; the thread-pool queue boundary; metric table with labels/units; OTLP endpoint/protocol, five-second export/scrape/evaluation cadence and naming translation; datasource/dashboard UIDs; mount separation, plugin choice, health checks and 11 panel purposes.
- [ ] Include the client-percentile caveat: use `http_client_duration_milliseconds_bucket`; the historical Locust duration histogram's seconds versus bucket-scale issue prevents its use for meaningful percentiles. Its `_count` remains the endpoint/failure counter. Preserve the server seconds-to-ms conversion and per-process `instance` separation. Revalidate this contract after package updates.
- [ ] Create `docs/development.md`: detailed setup, `LOCUSTFILE`/OTEL/Grafana override matrix, scaling/stop procedures, scenario and API extension instructions, thresholds and default-disable values, report paths, troubleshooting, and evidence/exception sections. Explain no-request failure, strict `>` comparisons and thresholds overriding Locust's default any-failure exit rule.
- [ ] Index the historical plan explicitly as a dated design/verification record. Retain its original bytes and the original PNG path. Do not invent a new screenshot, report or benchmark.
- [ ] Verify every preservation-map row, local path/anchor and code fence. Render the root diagram and inspect the landing-page image/text hierarchy. A missing paragraph, altered diagram relationship or buried flagship explanation blocks completion of this task.
- [ ] Commit documentation as a separate reviewable change after applicable checks. Later tasks may update tooling commands and evidence in the same guides.

## Task 2: Lock dependencies while preserving container and local entry points

**Interfaces:** Consume unchanged functional paths and Python 3.13; produce one root dependency authority and two reproducible requirements exports. Existing `app`, `steady` and `spike` module discovery remains intact.

- [ ] Review current compatible stable releases using official registries/release notes at execution time. Record candidates, chosen versions and compatibility constraints. Review the Locust package, OTEL-enabled image and instrumentation together; no runtime-major change or blind image upgrade.
- [ ] Create `.python-version` for 3.13 and a non-packaged `pyproject.toml` with `requires-python = ">=3.13,<3.14"`. Declare Flask, gunicorn and prometheus-client as default dependencies; `load-test` group contains Locust and pytest; `dev` contains Ruff, mypy, pre-commit and required typing support. Include the load-test group in the developer install.
- [ ] Generate and commit `uv.lock` with stable compatible releases. Pin the uv tool version used locally/CI and document it. Configure Ruff target `py313`, line length 120 and lint rules `E4`, `E7`, `E9`, `F`, `I`; configure mypy to check `target-app/` and `locustfiles/` with the runner import path. Use checked function bodies and explicit types at threshold/event/API boundaries; narrowly document unsupported third-party typing, never blanket-ignore first-party files.
- [ ] Generate `target-app/requirements.txt` from default runtime dependencies and `requirements-dev.txt` from defaults plus `load-test`, with hashes and generated-file headers. Use locked exports with the project omitted. Record exact export commands and add a CI drift check that regenerates into temporary files and compares both committed exports.
- [ ] Keep Docker build context `./target-app`; consume the exported requirements with hash enforcement. Preserve the gunicorn command and Python 3.13 baseline. Keep the existing pip developer entry point working with the generated dev requirements, while documenting uv as the primary workflow.
- [ ] Verify from a clean environment: `uv sync --locked`, `uv run pytest -q`, `uv run locust -f locustfiles/spike.py --list`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy target-app locustfiles`. Expect existing behavior tests to pass and `ApiUser` to be discoverable; resolve typing/formatting issues without semantic rewrites.
- [ ] Build the app and run the existing steady/full-stack checks before accepting dependency changes. If an updated compatibility set breaks OTLP, thresholds, provisioning or saturation, select the last compatible stable set and document the constraint, owner and review trigger. Failing verification is not an approved exception.
- [ ] Commit dependencies, generated exports and required source/tooling alignment together; update README versions/commands only from the verified choices.

## Task 3: Add fast, staged quality checks

**Interfaces:** Consume locked tool versions from Task 2; produce staged checks and equivalent full-check commands. No Docker, tests or live services in commit hooks.

- [ ] Create `.markdownlint-cli2.jsonc` with default rules enabled and only `MD013` disabled. Select root maintained Markdown and current guides; exclude `.venv`, generated reports and historical `docs/superpowers/` records without excluding current guides.
- [ ] Use one pinned markdownlint-cli2 version with Node 24 for local/CI execution. Document an exact-version local CLI command; no application `package.json` or Node application conversion is needed.
- [ ] Create `.pre-commit-config.yaml` using the existing locked Ruff through local system hooks (`uv run --locked ruff check`, `uv run --locked ruff format --check`) and pinned Markdown/config/text checks. Use staged filenames, default check mode and no auto-staging.
- [ ] Enable YAML/strict-JSON syntax, merge conflict, final newline and trailing-whitespace checks for their actual formats. Permit Compose anchors and preserve Markdown hard breaks; JSONC must not be passed to the strict-JSON hook. Ignore only generated/dependency/history content appropriate to each check.
- [ ] Update `.gitignore` only for introduced cache/output paths. Document `uv run pre-commit install` and `uv run pre-commit run --all-files`.
- [ ] In a disposable Git repository, prove bad staged Python/Markdown/YAML/JSON/conflict markers block commits; valid Compose YAML passes; intentional Markdown breaks pass; unstaged/untracked files do not widen staged checks; partial staging preserves unrelated working-tree content. Do not bypass failed hooks.
- [ ] Run all maintained-file checks and commit the hook/config changes using the installed hook.

## Task 4: Harden CI and validate configuration behavior

**Interfaces:** Consume the locked installs and checks from Tasks 2–3; preserve `.github/workflows/load-test.yml`, workflow `Load test`, existing load-test job identity, artifact `locust-report`, dashboard UID `load-test` and datasource UID `prometheus`.

- [ ] Add an independent job named `Offline quality` in the existing workflow: locked cached uv install on Python 3.13; full Ruff lint/format, mypy, maintained Markdown and configuration/text checks; pytest; export-drift checks. Use exactly the same commands and versions locally and in CI.
- [ ] Keep the existing `Unit tests, stack check and gated load test` job and its full-stack behavior. Install test dependencies through the locked uv environment; preserve its four nonempty metric queries, datasource-health probe, 11-panel check, autostart stop, gated run, result table and artifact.
- [ ] Resolve all action references, including any added uv/setup/lint actions, to verified full commit SHAs with readable version comments. Retain `pull_request`, `contents: read` and the existing job timeout; set a finite timeout on the added job and `persist-credentials: false` on every checkout. Set report retention to three days and state it in development docs.
- [ ] Keep failures visible: no `continue-on-error`, empty tests or unconditional success. Publish available reports/logs on failure and always tear down the CI-owned stack. If stats were not produced, report that explicitly without obscuring the original failed step.
- [ ] Run `docker compose config --quiet`; validate Prometheus configuration and rules using promtool from the selected pinned Prometheus image; parse dashboard JSON and inspect all PromQL sources/units rather than relying only on panel count.
- [ ] Add `tests/prometheus-alerts.yml` with synthetic promtool rule tests: target down fires after its 15-second hold; sustained client p95 over 500 ms fires after the hold; sustained server 5xx share over 5% fires after the hold; healthy and exact-boundary inputs do not fire. Run `promtool test rules` locally and in the stack job. Do not add a new production error endpoint just to fire an alert.
- [ ] Create weekly Dependabot updates for Python and `github-actions`. Verify current updater support for the root uv project and the separate Docker build context; configure supported Docker updates and document any Compose-image update gap and manual review trigger. Avoid duplicate independently managed generated requirements updates; group compatible minor/patch changes and require major-version review.
- [ ] Validate workflow syntax, configured Markdown scope, full-file checks and actual negative exit behavior. Read remote check/protection/scanning availability without mutation; record exact observed/proposed check names and owner actions. Workflow presence does not establish enforced branch protection.
- [ ] Commit CI/update configuration and supporting behavioral fixtures with fresh command evidence.

## Task 5: Verify the complete adoption and preserve the flagship outcome

**Interfaces:** Consume all changes above; produce dated evidence, a lossless documentation reconciliation and a review-ready branch. No merge or settings change.

- [ ] Repeat the documented developer setup from a clean checkout: locked install, full hook checks, lint/format/type/Markdown, unit tests, exports, Compose config and promtool config/rule tests. Record actual results rather than copying the historical `24 passed` observation.
- [ ] Start an isolated, task-owned Compose project after checking port availability; do not stop another running stack to obtain ports. Verify healthy app/Prometheus/Grafana, running master/worker, automatic 20-user load, anonymous dashboard access and all 11 panels populated. Record actual Python/container versions.
- [ ] Verify all four existing metric families reach Prometheus. Scale to two workers and demonstrate two active worker `instance` values with a total master user count of 20. Restore one worker before measuring the spike and confirming the baseline screenshot story.
- [ ] Stop autostarted load before the standalone gate. Run a 60-second/20-user/5-spawn-rate test against `http://localhost:5001` with `--max-p95-ms 500 --max-fail-ratio 0.01`, HTML and CSV under ignored `reports/`; expect exit 0 and nonzero requests. Run a deliberately low p95 limit of 50 ms against simulated API work; expect exit 1. Existing tests must still prove no-request failure, tolerable-failure success and thresholds-off behavior.
- [ ] Run a bounded spike verification through the 50-to-200-to-10 transition. Observe client/server p95 separation, latency-alert pending/firing and recovery after load reduces; allow histogram/window lag. Preserve the historical approximate numbers without claiming every host must reproduce them exactly. Stop explicitly: the shape repeats and must not rely on a headless run-time flag for termination.
- [ ] Stop only the task-owned app to verify `TargetAppDown`, then restart and confirm recovery. Verify `HighServerErrorRate` with the synthetic rule fixture. Record which alerts were tested live versus synthetically. Tear down the task-owned stack even on failure.
- [ ] Compare original/final README side by side. Check every preservation-map item, all moved links/anchors, root and deep diagrams, full screenshot prominence, scenario/alert/result details and the first-run path. Confirm PNG and historical-plan hashes match the baseline exactly. New command changes must have successful execution evidence or explicit outstanding status.
- [ ] Record revision/date/environment/commands/results in `docs/development.md`; distinguish historical observations, fresh local checks, hosted checks and owner settings. Record authorized exceptions with reason, owner and review trigger; unresolved failures remain pending rather than being relabeled compliant.
- [ ] Prepare metadata proposals for owner review: description no longer than 110 characters; no more than eight ordered topics. Suggested description: `Compares client and server latency with Locust, OpenTelemetry, Prometheus and Grafana`. Suggested topics: `test-automation`, `python`, `locust`, `grafana`, `opentelemetry`, `prometheus`, `load-testing`. Inspect current metadata first and do not apply changes as a side effect.
- [ ] Review the final diff for unnecessary source churn, loosened thresholds, removed content, lock/export drift or degraded presentation. Summarize the concrete changes before any separately authorized push/PR. Keep actual-head hosted results distinct from earlier runs; do not merge, change settings or start another repository.

## Completion criteria

- [ ] The owner can trace every original documentation fact to retained landing-page content or an indexed guide/history location; nothing unique disappears.
- [ ] The README retains its client/server latency narrative, screenshot, badges, root diagram, practical quickstart, scenarios, alerts, report evidence, stack and layout.
- [ ] The `complete` profile and exact standards pin are recorded outside the landing-page narrative.
- [ ] Python 3.13, the five-service design, measurement boundaries, load shape and existing threshold semantics remain intact.
- [ ] Locked dependency installs/exports, staged hooks, full CI checks, weekly updates and controlled stack verification have evidence or explicitly recorded pending work.
- [ ] Protection/scanning/metadata proposals, hosted checks and any unavailable environment work are clearly separated from verified implementation.

## Planning verification

This plan was based on local inspection of all 21 tracked baseline files, including the complete historical plan, current workflow, Python sources/tests, provisioning, Prometheus rules, dashboard JSON and the rendered PNG. The PNG visibly shows 200 users, 884 ms client p95, 235 ms server p95 and one firing alert. Those are observations of the existing image, not a fresh benchmark. No package freshness audit, test execution, Docker run or remote/settings inspection was performed during planning.

Only this plan is added by the planning task. Review the plan before implementation.

## Execution status — 2026-10-31

The owner authorized execution with “Proceed”. See [development evidence](../../development.md#adoption-evidence-and-pending-work) for commands, environments and limitations.

| Task | Status |
| --- | --- |
| 1: Documentation | Guides and agent guidance added; showcase retained, CI descriptions updated per owner instruction; protected PNG/history unchanged; cloud rendering verified |
| 2: Dependencies | Python baseline, typing, tool configuration, uv lock, hashed exports and cloud locked installs implemented; application/image baselines deliberately retained |
| 3: Staged gates | Implemented and verified with actual commit probes and full-file checks |
| 4: CI | Cloud quality and documentation rendering pass; Docker/promtool/Locust checks moved to local script as instructed |
| 5: Verification | Offline/runtime checks, locked cloud quality, rendering and isolated local-script probes pass; live local Docker/load/telemetry/alerts and owner settings review remain pending |

The earlier requirements fallback was replaced by the committed uv lock and hashed exports. PR #5 is open; no merge or remote settings change was performed. Live local checks remain explicitly unverified in this restricted host.

## Superseding owner instruction: execution placement

Docker and the Locust runner must run locally. The cloud workflow now runs only
unit tests and code/documentation/configuration quality checks. The former stack
job's configuration validation, telemetry probes, gated load run and result table
are retained in `scripts/verify-stack.sh` with local reports and owned cleanup.
This explicit instruction supersedes references above to a hosted stack/load job,
uploaded load artifacts and a required hosted integration check.

## Dependency completion and PR publication

The owner authorized completing the work and creating a PR. [PR #5](https://github.com/yashwant-das/qa-py-locust-grafana/pull/5) is open. Its initial service-free quality job passed; a temporary resolver generated `uv.lock` and both hashed exports with uv 0.13.6. The final workflow removes the resolver, installs with `uv sync --locked` and checks export drift. This supersedes the earlier pending-lock/fallback status. Docker/load verification remains local by explicit instruction.

## Final handoff verification

The locked cloud quality and documentation diagram jobs both passed in run `41211367229`; all three rendered previews were inspected. The temporary dependency resolver and preview-transfer step were removed. Only service-free quality and documentation rendering remain in cloud CI; local Docker/load/alert execution is documented separately. The protected screenshot and historical plan retain their original hashes.
