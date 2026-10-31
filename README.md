# Load Testing & Observability with Locust, Prometheus and Grafana

Distributed load testing with Locust against a sample Flask API, with the client's view and the server's view of the same test on one Grafana dashboard, all in one Docker Compose stack.

[![Quality checks](https://github.com/yashwant-das/qa-py-locust-grafana/actions/workflows/load-test.yml/badge.svg)](https://github.com/yashwant-das/qa-py-locust-grafana/actions/workflows/load-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Locust](https://img.shields.io/badge/Locust-2.46-2F7D32)](https://locust.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-3.15-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-13.2-F46800?logo=grafana&logoColor=white)](https://grafana.com)

## Why it exists

A load test result is only useful next to what the system was doing at the time. Locust reports what each simulated user experienced. The app reports how long it spent handling each request. This repo puts both on one dashboard, so the gap between them is visible.

The spike scenario shows why that matters. At 200 users, Locust's p95 response time climbs to about one second while the app still reports about 240 ms. The requests are waiting in a queue for one of the app's 8 worker threads, and the app's own numbers cannot show time spent before a request reaches it.

What this project demonstrates:

- Distributed Locust workers with built-in OpenTelemetry export, without a separate exporter.
- Client and server measurements on one provisioned dashboard, exposing queueing hidden from handler timings.
- Expected-negative API requests that count as successes, alongside configurable latency/failure gates.
- A complete local stack and reproducible gated load test, with service-free quality checks in GitHub Actions.

## Dashboard and metrics

These screenshots show the stack at different load levels. The values are examples from those captures; results depend on the load and the machine running the services.

### Grafana: client vs server latency

The provisioned **Load test: client vs server** dashboard compares both sides of a request. During the captured 200-user spike, it shows 46.2 requests/s, client p95 at 884 ms, server p95 at 235 ms and one firing alert. The latency gap illustrates time spent waiting before a handler starts.

![Grafana dashboard during a 200-user spike, showing client p95 of 884 ms and server p95 of 235 ms](docs/dashboard.png)

### Prometheus: request rate by endpoint

Prometheus receives Locust's client metrics over OpenTelemetry and scrapes the app's `/metrics` endpoint. This graph shows the five Locust request names, with rates averaged over five minutes. In this capture, `/users` is around 4.3 requests/s, `/users/[id]` around 2.1 and `/users [create]` around 1.5.

![Prometheus graph showing request rates for the five Locust request names](docs/prometheus-query-graph.png)

See the [Prometheus queries](#prometheus-queries) below to reproduce this view and compare client and server latency.

### Locust: request statistics

The master's statistics tab shows request counts, failures, median, p95, p99, average, minimum and maximum response times, and current request rates. This capture shows the default 20-user load at 9.4 requests/s with no failures.

![Locust statistics for 20 active users, showing 9.4 requests/s, no failures and latency by request name](docs/locust-webui.png)

## Architecture

```mermaid
flowchart LR
    Master[Locust master<br/>web UI :8089] --> Workers[Locust workers]
    Workers -->|HTTP load| App[Target app<br/>Flask :5001]
    Workers -->|request metrics, OTLP| Prom[Prometheus :9090]
    Master -->|user count, OTLP| Prom
    Prom -->|scrapes /metrics every 5s| App
    Grafana[Grafana :3000] -->|queries| Prom
```

Locust workers send load to the target app and push their own request metrics to Prometheus over OpenTelemetry (`locust --otel`). Prometheus also scrapes the app's `/metrics` endpoint and evaluates the alert rules. Grafana reads from Prometheus through a provisioned datasource and dashboard.

## Quickstart

Prerequisites: Docker with Compose v2, and free ports 3000, 5001, 8089 and 9090. Local Python verification uses Python 3.13; the Docker quickstart needs no local Python installation.

```bash
git clone https://github.com/yashwant-das/qa-py-locust-grafana.git && cd qa-py-locust-grafana
docker compose up --build -d --wait
```

A 20-user test starts by itself. Open <http://localhost:3000> and the dashboard is already moving. No login or setup is needed.

| Service | URL | Notes |
| --- | --- | --- |
| Grafana | <http://localhost:3000> | Opens on the dashboard with anonymous read-only access. Sign in as `admin` / `admin` to edit. |
| Locust web UI | <http://localhost:8089> | Stop the test, or start a new one with a different user count |
| Prometheus | <http://localhost:9090> | Queries, targets and alerts |
| Target app | <http://localhost:5001> | The `/users` API, `/health` and `/metrics` |

All four ports are bound to `127.0.0.1` only. Add workers with `docker compose up -d --scale locust-worker=4`. Stop everything with `docker compose down`.

## Scenarios

| Scenario | File | What it does |
| --- | --- | --- |
| Steady load (default) | `locustfiles/steady.py` | 20 users reading and creating users, including an expected 404 and an expected 400 |
| Spike | `locustfiles/spike.py` | The same users on a repeating 5-minute shape: 2 minutes at 50 users, 1 minute at 200, 2 minutes at 10 |

Switch scenario with the `LOCUSTFILE` variable:

```bash
LOCUSTFILE=spike.py docker compose up -d
```

The 200-user phase starts two minutes into each cycle. During that phase, client p95 can rise above 500 ms while server handler latency stays much lower. `HighClientLatency` fires after its measured p95 remains above 500 ms for 15 seconds; the rolling measurement window and rule evaluation affect the exact firing time.

See [Dashboard and alerts](#dashboard-and-alerts) for all three rules. A normal spike does not itself trigger `TargetAppDown`: that rule detects a failed app scrape.

## Prometheus queries

Open the [Prometheus query page](http://localhost:9090/query), paste one expression at a time, and choose **Table** for current values or **Graph** for changes over time. Run load before querying request metrics. Rate and percentile queries need multiple samples; idle or missing series can produce an empty result or `NaN`.

### Service health and active users

Check whether Prometheus can scrape the target app:

```promql
up{job="target-app"}
```

`1` means the scrape succeeded; `0` means it failed. This checks the app scrape, not the health of every service.

Count active users across Locust user classes:

```promql
sum(locust_users_count)
```

The default autostarted test runs 20 users. The spike scenario changes that count over its cycle.

### Client request rates

Request rate by Locust request name, summed across workers, in requests/s:

```promql
sum by (name) (rate(locust_client_duration_seconds_count[5m]))
```

This is the query used in the [Prometheus screenshot](#prometheus-request-rate-by-endpoint). The shared user class has five request names: `/users`, `/users/[id]`, `/users [create]`, `/users [invalid]` and `/users/[missing]`. Their rates vary with task selection and response time.

Rank the five busiest request names:

```promql
topk(5, sum by (name) (rate(locust_client_duration_seconds_count[5m])))
```

The five-minute window smooths changes in load; a shorter window responds more quickly to the one-minute spike.

### Client latency and response counts

Client p95 in milliseconds, including time spent waiting before the app handles a request:

```promql
histogram_quantile(
  0.95,
  sum by (le) (rate(http_client_duration_milliseconds_bucket[30s]))
)
```

Use this millisecond histogram for client percentiles. The Locust-specific duration counter above is useful for request rates; its histogram bucket scale is unsuitable for these percentiles in the retained instrumentation version.

Cumulative GET/POST request counts, grouped by HTTP status:

```promql
sum by (http_status_code) (
  http_client_duration_milliseconds_count{
    http_status_code=~"2..|404",
    http_method=~"GET|POST"
  }
)
```

This example includes successful 2xx responses and expected 404 reads. It deliberately filters out 400 responses; add `400` to the status regex to include invalid-body requests. Counts increase over a process's lifetime and can reset when it restarts; they are not request rates.

### Server request rates and latency

Request rate by HTTP method and route, in requests/s:

```promql
sum by (method, route) (
  rate(app_http_request_duration_seconds_count[5m])
)
```

Server p95 by method and route, converted from seconds to milliseconds:

```promql
1000 * histogram_quantile(
  0.95,
  sum by (le, method, route) (
    rate(app_http_request_duration_seconds_bucket[30s])
  )
)
```

Grouping by method separates GET and POST requests to `/users`. Compare these handler timings with client p95 during the spike: queueing before a handler starts contributes to the client measurement but not the app's timer. Routes without recent observations do not have a meaningful percentile.

### Server response counts and alerts

Cumulative app response counts by status:

```promql
sum by (status) (app_http_request_duration_seconds_count)
```

The scenario exercises 200 and 201 responses, plus expected 400 and 404 responses. Those expected negative responses are marked successful by the corresponding Locust tasks.

Inspect active alert states:

```promql
ALERTS{alertname=~"HighClientLatency|TargetAppDown|HighServerErrorRate"}
```

The `alertstate` label distinguishes pending and firing alerts. There are no active series when all rules are inactive. `HighClientLatency` can activate at any user count if its latency condition holds; the spike is the included scenario that demonstrates it.

## Test reports and results

Cloud CI runs unit tests, lint, formatting, type checking and documentation/configuration checks on every push and pull request. Docker services and Locust load runs execute locally.

After the [developer setup](docs/development.md#setup), run the complete local verification:

```bash
bash scripts/verify-stack.sh
```

It starts the full stack, checks that Locust and app metrics reach Prometheus and that Grafana has loaded the dashboard, then runs a 60-second, 20-user headless test. The gate fails if p95 exceeds 500 ms or more than 1% of requests fail. The script stops its own stack when it finishes.

Results are written locally to `reports/locust-summary.md`, `reports/locust-report.html` and `reports/locust_*.csv`. [Quality check runs](https://github.com/yashwant-das/qa-py-locust-grafana/actions/workflows/load-test.yml) show the cloud checks; load reports are generated by the local run.

The thresholds are command-line options added by `steady.py`, so the same gate runs locally against the stack:

Stop the autostarted test in the Locust UI (or with `curl -f http://localhost:8089/stop`) before running this standalone gate, so the two loads do not compete.

```bash
pip install -r requirements-dev.txt
locust -f locustfiles/steady.py --headless --users 20 --spawn-rate 5 --run-time 60s \
  --host http://localhost:5001 --max-p95-ms 500 --max-fail-ratio 0.01 --html report.html
```

### Offline verification

After the [developer setup](docs/development.md#setup), check Python and documentation without starting Docker:

```bash
uv run --locked --no-sync ruff check .
uv run --locked --no-sync ruff format --check .
uv run --locked --no-sync mypy target-app locustfiles
uv run --locked --no-sync pytest -q
uv run --locked --no-sync pre-commit run --all-files
```

These checks cover code, API/metrics behavior, threshold exits and maintained documentation. The separate local stack check verifies Docker wiring, telemetry delivery and the controlled load gate. See [development](docs/development.md) for configuration, quality gates, local reports and troubleshooting.

### Dashboard and alerts

There is one dashboard, **Load test: client vs server**. It shows users, request rate, p50 and p95 from both sides, failed requests and firing alerts, with breakdowns by endpoint, status code and route.

Alert rules live in `grafana/prometheus/alert_rules.yml`:

| Alert | Fires when |
| --- | --- |
| `TargetAppDown` | Prometheus cannot scrape the app for 15 seconds |
| `HighServerErrorRate` | More than 5% of the app's responses are 5xx for 15 seconds |
| `HighClientLatency` | Locust's p95 response time is above 500 ms for 15 seconds |

Firing alerts show on the dashboard and at <http://localhost:9090/alerts>. There is no Alertmanager, so nothing is sent anywhere.

## Tech stack

| Layer | Tool | Version | Why |
| --- | --- | --- | --- |
| Load generation | Locust, master and workers | 2.46.7 | Python scenarios, distributed load, built-in OpenTelemetry export |
| Target app | Flask on gunicorn, prometheus-client | 3.1.3, 26.2.0, 0.26.0 | Small API with a latency histogram per method, route and status |
| Metrics | Prometheus | 3.15.0 | Scrapes the app, receives Locust's metrics over OTLP, evaluates alert rules |
| Dashboards | Grafana | 13.2.3 | Provisioned datasource and dashboard |
| Orchestration | Docker Compose, GitHub Actions | v2 | Local stack and gated load tests; service-free quality checks in CI |
| Language | Python | 3.13 | Target app, scenarios and tests |

## Project structure

```text
├── locustfiles/
│   ├── steady.py            # The user behaviour and the pass/fail thresholds
│   └── spike.py             # The same users with a repeating spike shape
├── target-app/              # Flask API with /health and /metrics
├── tests/                   # Unit tests for the app and the thresholds
├── grafana/
│   ├── dashboards/          # The dashboard JSON
│   ├── provisioning/        # Datasource and dashboard provisioning
│   └── prometheus/          # prometheus.yml and alert_rules.yml
├── docker-compose.yml
├── requirements-dev.txt     # Locust, pytest and quality tools for local runs and CI
├── scripts/verify-stack.sh  # Local stack, telemetry and gated load verification
├── pyproject.toml           # Python baseline, direct dependencies and tool settings
├── AGENTS.md                # Agent guidance
└── docs/                    # Architecture, development and historical design records
```

## Documentation

| Guide | Contents |
| --- | --- |
| [Architecture](docs/architecture.md) | Service lifecycles, metric sources/units, queueing boundaries and provisioning |
| [Development](docs/development.md) | Setup, overrides, extending scenarios, gates, troubleshooting and verification evidence |
| [Historical stack design](docs/superpowers/plans/2026-10-12-simplify-load-test-stack.md) | Original implementation rationale, commands and dated observations; retained as history |

## License

MIT. See [LICENSE](LICENSE).
