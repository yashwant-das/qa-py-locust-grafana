#!/usr/bin/env bash
# Local Docker/load verification. Cloud CI runs service-free quality checks.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
for tool in docker curl jq uv; do
  command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 1; }
done
docker info >/dev/null

# Own only this invocation's containers; published ports must already be free.
project="locust-verify-$$"
export LOCUSTFILE=steady.py
compose() { docker compose -p "$project" "$@"; }
cleanup() {
  status=$?
  trap - EXIT
  if [ "$status" -ne 0 ]; then compose logs --tail 100 || true; fi
  if ! compose down; then status=1; fi
  exit "$status"
}
trap cleanup EXIT

compose config --quiet
docker run --rm --entrypoint promtool \
  -v "$PWD/grafana/prometheus:/etc/prometheus:ro" \
  prom/prometheus:v3.15.0 check config /etc/prometheus/prometheus.yml
docker run --rm --entrypoint promtool -v "$PWD:/work:ro" -w /work \
  prom/prometheus:v3.15.0 test rules tests/prometheus-alerts.yml
compose up --build --detach --wait

query_has_data() {
  curl -sfG http://localhost:9090/api/v1/query --data-urlencode "query=$1" \
    | jq -e '.data.result | length > 0' >/dev/null
}
for query in \
  'locust_users_count > 0' \
  'http_client_duration_milliseconds_count' \
  'locust_client_duration_seconds_count' \
  'app_http_request_duration_seconds_count'; do
  for attempt in $(seq 1 30); do
    query_has_data "$query" && break
    sleep 2
  done
  query_has_data "$query" || { echo "No data in Prometheus for: $query" >&2; exit 1; }
  echo "ok: $query"
done
curl -sf http://localhost:3000/api/datasources/uid/prometheus/health >/dev/null
curl -sf http://localhost:3000/api/dashboards/uid/load-test \
  | jq -e '.dashboard.panels | length == 11' >/dev/null
echo "ok: Grafana can query Prometheus and the dashboard is loaded"

curl -sf http://localhost:8089/stop
mkdir -p reports
load_status=0
uv run --locked --no-sync locust -f locustfiles/steady.py \
  --headless --users 20 --spawn-rate 5 --run-time 60s \
  --host http://localhost:5001 --max-p95-ms 500 --max-fail-ratio 0.01 \
  --html reports/locust-report.html --csv reports/locust --only-summary || load_status=$?

uv run --locked --no-sync python - <<'PY' > reports/locust-summary.md
import csv
from pathlib import Path

columns = ["Type", "Name", "Request Count", "Failure Count", "50%", "95%", "99%", "Requests/s"]
print("# Locust results (response times in ms)\n")
print("| " + " | ".join(columns) + " |")
print("|" + " --- |" * len(columns))
with Path("reports/locust_stats.csv").open() as stats:
    for row in csv.DictReader(stats):
        row["Requests/s"] = f"{float(row['Requests/s']):.1f}"
        print("| " + " | ".join(row[column] for column in columns) + " |")
PY
echo "Reports: reports/locust-report.html, reports/locust_*.csv, reports/locust-summary.md"
exit "$load_status"
