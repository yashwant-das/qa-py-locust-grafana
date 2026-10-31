# Development

Run commands from the repository root. The [README](../README.md) remains the
quickstart and showcase; [architecture](architecture.md) explains measurements,
service boundaries and design choices.

## Setup

Docker with Compose v2 runs the demo. Local Python checks use Python 3.13 and
[uv 0.13.6](https://docs.astral.sh/uv/getting-started/installation/). Markdown hooks
use Node 24.22.1 in a pre-commit-managed environment; Node is tooling, not an app
runtime. Installation requires network access; checks need no secrets or services
after their dependencies and hook environments are installed.

```bash
uv venv --python 3.13
uv pip sync requirements-dev.txt
uv run --no-sync pre-commit install
uv run --no-sync pre-commit install-hooks
```

The requirements install path remains available without uv:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

The repository is a non-packaged, multi-service project. `pytest.ini` keeps
`target-app` and `locustfiles` on the import path and discovers `tests/`. Do not
turn those functional folders into a distributable package just for uniformity.

### Dependency sources and current limitation

[pyproject.toml](../pyproject.toml) records direct dependencies and tool settings.
The two fully pinned requirements files currently preserve the working pip/Compose
workflow: [runtime](../target-app/requirements.txt) contains the app's dependency
closure; [development](../requirements-dev.txt) includes it and adds the load-test
and quality-tool closures. Docker retains its standalone `./target-app` context.
Use `uv pip check` after installation to reject dependency conflicts.

The planned uv lock and hash-bearing exports remain **pending**, not an approved
exception or a claim of complete dependency adoption. Shell DNS prevented registry
resolution, and uv 0.13.6 could not read the older cached Flask/Locust registry
metadata. Do not run `uv sync` or plain `uv run` expecting a committed lock; use
`uv run --no-sync` with the installed requirements environment for now.

At the next network-enabled dependency review, resolve `uv.lock` on Python 3.13,
sync from it, generate both requirements exports with hashes and `--locked
--no-emit-project` (runtime: `--no-dev`; developer: `--all-groups`), compare generated
exports in CI and switch hooks/CI to locked project installs together. Owner:
Yashwant Das; trigger: network-enabled clean install and full-stack verification.
Keep the requirements install until that migration is verified.

Existing app/image versions were retained because their OTLP and saturation
compatibility cannot be re-proven without Docker. New tools are Ruff 0.17.1,
mypy 2.4.0 and pre-commit 4.7.0. Official [Ruff](https://pypi.org/project/ruff/0.17.1/),
[mypy](https://pypi.org/project/mypy/2.4.0/) and
[pre-commit](https://pypi.org/project/pre-commit/4.7.0/) pages were inspected; mypy
2.4.1 was available but unavailable in the local cache. Current-version selection,
package advisory review and fresh installs remain pending; no latest-version or
security-clearance claim is made.

Update direct pins, their resolved requirements closures, images where applicable
and affected README versions together. Test package metadata and both runtime and
developer environments before accepting updates. Do not manually loosen a pin to
make a test pass. Weekly Dependabot PRs cover pip, GitHub Actions, the target
Dockerfile and Compose images; major updates require explicit compatibility review.
The eventual uv migration must change the Python updater ecosystem at the same time.

## Local quality checks

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync mypy target-app locustfiles
uv run --no-sync pytest -q
uv pip check
uv run --no-sync pre-commit run --all-files
```

Ruff uses Python 3.13, a 120-character line length, its default error rules and
import sorting. Mypy checks the app and both scenario modules, including function
bodies and explicit API/threshold/event boundaries. No first-party files or
third-party imports are blanket-excluded from the configured type check. Tests exercise real Locust statistics and event behavior.

Hooks check staged Python, Markdown, TOML, YAML, strict JSON and text. Markdown
hard breaks are preserved; JSONC is not fed to strict JSON parsing. The Markdown
baseline enables default rules except line length; historical plans, dependency
folders and generated reports are excluded. Current guides are included.
Review and restage any hook fixes yourself; do not bypass failed hooks or stage
unrelated edits. Full tests/type checking and Docker stay outside commit hooks.

For Markdown alone, run `uv run --no-sync pre-commit run markdownlint-cli2
--all-files`. An equivalent CLI is `npx --yes --package=markdownlint-cli2@0.24.0
markdownlint-cli2 README.md AGENTS.md 'docs/*.md'`. Use Node 24; the pinned hook
installs its own Node and uses the same `.markdownlint-cli2.jsonc` configuration.

## Stack configuration

```bash
docker compose config --quiet
docker compose up --build -d --wait
docker compose up -d --scale locust-worker=4
docker compose down
```

Check port availability before starting. Do not stop an unrelated stack to free
ports. A dedicated Compose project (`docker compose -p locust-review …`) isolates
service ownership but does not change the published ports.

| Setting | Default | How it is used |
| --- | --- | --- |
| `LOCUSTFILE` | `steady.py` | Compose selects a file from the read-only `locustfiles` mount |
| Master users/spawn rate | 20 / 5 per second | Compose master command; web UI can stop/restart load |
| Target inside Docker | `http://target-app:5000` | Worker traffic; local headless runs use `http://localhost:5001` |
| Published ports | 3000, 5001, 8089, 9090 | All bind `127.0.0.1` |
| OTLP protocol | `http/protobuf` | Locust OTEL-enabled image and `--otel` |
| OTLP metric endpoint | `http://prometheus:9090/api/v1/otlp/v1/metrics` | Shared master/worker environment |
| OTLP metric export interval | `5000` ms | Shared master/worker environment |
| Trace/log exporters | `none` | Metrics only |
| Grafana anonymous access | enabled, `Viewer` | No login to read; `admin` / `admin` edits locally |
| Grafana home dashboard | `/var/lib/grafana/dashboards/load_test.json` | File-provisioned landing page |
| Grafana plugin preinstall | disabled | Keeps bundled datasource plugins available during startup |

To change tracked service settings, edit Compose or use an explicitly selected
Compose override file. Only `LOCUSTFILE` is interpolated from the host by the
current Compose file; exporting another variable alone does not override it.
The default `.env` file can supply `LOCUSTFILE`; do not commit secrets.

## Scenarios and extension

`steady.py` owns `ApiUser`, task weights, negative-response expectations and
pass/fail options. Add tasks there when both scenarios should use them; keep
request names stable so endpoint cardinality stays bounded. For a new route,
extend the target API and its behavior/metrics tests together. Verify malformed
bodies, status expectations and route-template labels.

`spike.py` imports `ApiUser` intentionally for Locust discovery and repeats a
300-second shape: 50 users for 120 seconds, 200 for 60, then 10 for 120. Spawn
rates are 10, 50 and 50 respectively. Verify discovery with:

```bash
uv run --no-sync locust -f locustfiles/spike.py --list
LOCUSTFILE=spike.py docker compose up -d --wait
```

Stop the spike explicitly with the UI or `docker compose down`. Its shape repeats;
do not assume a headless `--run-time` bounds it. The original latency alert fired
roughly 25 seconds into the spike; measurement/window timing varies by host.

### Thresholds and reports

| Option or case | Behavior |
| --- | --- |
| `--max-p95-ms` | Default `0` disables the latency limit; breaches use strict `>` |
| `--max-fail-ratio` | Default `1` disables the failure-share limit; breaches use strict `>` |
| Both limits disabled | Leaves Locust's original process exit code unchanged |
| Any limit enabled | Limits decide exit 0/1, including allowing failures within the configured share |
| No requests in a gated run | Fails, even though empty statistics could otherwise look healthy |
| Expected 404/400 | Successful requests when their task-specific expectations are met |

Stop the autostarted test before a standalone test, so they do not compete for the
same eight server threads:

```bash
curl -f http://localhost:8089/stop
mkdir -p reports
uv run --no-sync locust -f locustfiles/steady.py \
  --headless --users 20 --spawn-rate 5 --run-time 60s \
  --host http://localhost:5001 --max-p95-ms 500 --max-fail-ratio 0.01 \
  --html reports/locust-report.html --csv reports/locust --only-summary
```

Expect nonzero requests and exit 0 if p95 stays at or below 500 ms and failure
share at or below 1%. A deliberate `--max-p95-ms 50` run should exit 1 against
the simulated work. The HTML report, CSV stats/history/failures and local summary
are generated output under ignored `reports/`; do not commit them.

## Configuration and alert verification

```bash
docker run --rm --entrypoint promtool \
  -v "$PWD/grafana/prometheus:/etc/prometheus:ro" \
  prom/prometheus:v3.15.0 check config /etc/prometheus/prometheus.yml
docker run --rm --entrypoint promtool -v "$PWD:/work:ro" -w /work \
  prom/prometheus:v3.15.0 test rules tests/prometheus-alerts.yml
```

The first validates scrape/OTLP/rule configuration and finds three rules. The
second exercises healthy, pending, firing, recovery and exact-threshold cases
with synthetic series. It does not prove live scrape or OTLP delivery.

For live wiring, query Prometheus for nonempty `locust_users_count > 0`,
`http_client_duration_milliseconds_count`, `locust_client_duration_seconds_count`
and `app_http_request_duration_seconds_count`. Check anonymous datasource health
at `/api/datasources/uid/prometheus/health` and dashboard provisioning at
`/api/dashboards/uid/load-test`; all 11 panels must contain data in the UI.

Scale to two workers, restart a 20-user swarm and query
`count(count by (instance) (rate(http_client_duration_milliseconds_count[20s]) > 0))`:
expect two active instances and `sum(locust_users_count)` equal to 20. Restore one
worker before reproducing the screenshot. During the spike, observe client p95
rise above server p95 and `HighClientLatency` progress pending → firing → recover.
Stop only the task-owned target to test `TargetAppDown`, then restart it. The 5xx
rule is tested synthetically; no artificial production endpoint is needed.

## CI and troubleshooting

The `Quality checks` workflow retains the existing `load-test.yml` file path so
badge and workflow URLs continue to work. Its only job, `Offline quality`, runs
unit tests, Ruff lint/format, mypy, dependency consistency and full-file hooks on
GitHub-hosted infrastructure. It starts no Docker service or Locust runner.

Run the controlled integration pipeline locally after developer setup:

```bash
bash scripts/verify-stack.sh
```

This checks Compose and Prometheus configuration, runs synthetic alert tests,
starts a uniquely named five-service Compose project, checks the four metric
families and Grafana provisioning, stops autostart and executes the 60-second
load gate. It requires Docker, curl, jq, uv and free default ports. Its exit trap
prints service logs on failure and tears down only its own project. It does not
replace the separate spike, two-worker and live-alert checks described above.

Local output is `reports/locust-report.html`, `reports/locust_*.csv` and
`reports/locust-summary.md`, with per-request and aggregate results. Outputs stay
on the local machine until removed; cloud CI no longer uploads load-report
artifacts or applies an artifact-retention period.

| Symptom | Check |
| --- | --- |
| Docker socket unavailable | Start your Docker runtime; `docker info` must succeed |
| Port already used | Inspect the owning process; choose an explicit override rather than stopping someone else's stack |
| Empty metrics | Inspect `/api/v1/label/__name__/values` and master/worker OTEL logs; confirm receiver endpoint/naming |
| Dashboard missing | Keep provisioning and dashboard mounts separate; inspect provider path and UID |
| Datasource intermittently missing at startup | Keep background plugin preinstallation disabled |
| Unexpected load-test failures | Stop competing autostart load; inspect actual failures, p95, queueing and limits |
| Spike never exits | Stop it explicitly; the custom shape repeats |
| Wrong client percentiles | Use the instrumentation's millisecond histogram, not the Locust seconds histogram |

## Adoption evidence and pending work

Profile: `complete`. Policy pin:
[`a429dd2f2da55a4c3e1c73c7c0d1111f9cd0b9a9`](https://github.com/yashwant-das/repo-standards/tree/a429dd2f2da55a4c3e1c73c7c0d1111f9cd0b9a9).
Execution began 2026-10-31 from `a7580551727e14352542f6208c109cb9aee595e9` on
`codex/adopt-repo-standards`. The GitHub connector confirmed that same `main` SHA
after the shell fetch failed DNS; no remote branch or settings mutation occurred.

The original showcase narrative, scenarios, thresholds, alerts, stack and quickstart
remain on the landing page. Following the owner's later instruction, descriptions
of CI-hosted Docker/load execution and uploaded artifacts now describe the local
verification script and local report paths; the earlier content-retention check
below predates that intentional scope change. The original PNG and 1,503-line historical plan remain
byte-for-byte intact. Current metric/lifecycle/operations details were carried
into these guides while preserving their original historical source.

| Check | Evidence/status |
| --- | --- |
| Baseline unit suite | Python 3.13.15, `.venv/bin/pytest -q`: 24 passed in 0.48 s before changes |
| Fresh unit/lint/format/types | Executable revision `805d828`: clean-checkout Python 3.13.15, 24 tests passed in 4.12 s; Ruff 0.17.1 lint/format and mypy 2.4.0 (all three app/scenario modules) pass |
| Staged and full-file hooks | All configured hooks pass; real commits exercise the installed hook; nine disposable probe outcomes cover blocking, valid inputs, staging and independent full-file checks |
| Clean dependency installs | Separate fresh 56-package developer and nine-package runtime environments installed offline from reconstructed cached wheel contents; `uv pip check` passes for both; this is not a fresh registry download |
| Runtime-only smoke | Fresh nine-package environment: gunicorn WSGI config, health, seeded/missing user, creation and metrics checks pass without network sockets |
| Dependency metadata | Installed dependency requirements satisfy Linux x86_64 and macOS arm64 Python 3.13 markers/specifiers; metadata-only Linux validation does not prove native-wheel execution |
| Compose/workflow/dashboard | `docker compose config --quiet`, YAML/JSON parsing, all action SHA pins, least privilege, checkout settings, job timeouts and embedded Bash syntax pass; dashboard still has 11 panels |
| Documentation retention | Every original README content block retained (requirements tree row expanded with quality tools); 18 local file/anchor links resolve; PNG and historical plan hashes match the base |
| New diagram visual rendering | Pending; no local Mermaid renderer was available. Root diagram source is unchanged |
| Fresh registry/uv lock/hash exports | Blocked by shell DNS and old cache metadata; pending dependency adoption |
| Docker build, promtool, live stack/spike/alerts/two-worker checks | Pending: Docker socket absent; `open -a Docker` could not locate an application. Native gunicorn binding to a task-owned loopback port also failed with sandbox `Operation not permitted` |
| Hosted checks on adoption head | Not run; no branch publication. Hosted scope is now only the service-free quality job |
| Repository enforcement and scanning | Availability/enforcement not yet verified; no settings changed |

Requirements fallback and unavailable checks are pending owner review, not approved
exceptions. Owner: Yashwant Das. Review triggers: restored registry access for the
dependency migration, working Docker for controlled integrations, and a published
review branch for current-head hosted checks. Keep implementation and evidence
status separate; this is not a full-compliance or merge-readiness claim. The
whole-branch review was performed inline, honoring this project's no-subagent
preference; independent review remains an owner decision.

Protected baseline SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `docs/dashboard.png` | `862c341397a0920fba1acad8559c86df977b14a5d0754e2bf0e6e0aa52063f4e` |
| Historical simplification plan | `e5eb0e0f7687647ea7debbd9b00dab22a352a2650b407b64a3c327f120a256d8` |

The proposed required cloud check is `Offline quality`; confirm its exact hosted
context name before applying rules. Docker/Locust integration is an owner-selected
local verification task, not a cloud or self-hosted Actions job.
Do not interpret workflow presence as required-check enforcement. Review secret
scanning and Python code-scanning availability before enabling them separately.

The current GitHub description is longer than 110 characters; topics contain
eight entries including `docker`. Proposed description: “Compares client and
server latency with Locust, OpenTelemetry, Prometheus and Grafana”. Proposed topics,
in order: `test-automation`, `python`, `locust`, `grafana`, `opentelemetry`,
`prometheus`, `load-testing`. These are proposals only.

### Owner clarification: local integration, cloud quality

The owner explicitly selected local execution for Docker and the load runner.
This supersedes the original adoption plan's CI integration placement. The full
stack, Prometheus rule checks, telemetry probes, latency/failure gate and report
summary are preserved in `scripts/verify-stack.sh`. The cloud workflow retains
all code-quality and unit checks. Existing live Docker verification remains
pending locally; it is no longer a hosted-CI requirement. The script passes Bash
syntax review but its live execution remains unverified in this restricted host.
