from types import SimpleNamespace

from locust.stats import RequestStats
from steady import apply_thresholds, threshold_breaches


def stats_with(response_times_ms, failures=0):
    stats = RequestStats()
    for response_time in response_times_ms:
        stats.log_request("GET", "/users", response_time, 0)
    for _ in range(failures):
        stats.log_error("GET", "/users", "boom")
    return stats


def quit_with(stats, max_p95_ms=0, max_fail_ratio=1):
    options = SimpleNamespace(max_p95_ms=max_p95_ms, max_fail_ratio=max_fail_ratio)
    environment = SimpleNamespace(parsed_options=options, stats=stats, process_exit_code=None)
    apply_thresholds(environment)
    return environment.process_exit_code


def test_passes_within_thresholds():
    assert threshold_breaches(stats_with([100] * 100).total, max_p95_ms=500, max_fail_ratio=0.01) == []


def test_reports_slow_p95():
    total = stats_with([100] * 90 + [900] * 10).total
    assert threshold_breaches(total, max_p95_ms=500, max_fail_ratio=1) == ["p95 900 ms is above 500 ms"]


def test_reports_failure_ratio():
    total = stats_with([100] * 100, failures=5).total
    assert threshold_breaches(total, max_p95_ms=0, max_fail_ratio=0.01) == ["failure ratio 5.0% is above 1.0%"]


def test_a_run_with_no_requests_is_a_breach():
    assert threshold_breaches(stats_with([]).total, max_p95_ms=500, max_fail_ratio=1) == ["no requests were made"]


def test_exit_code_is_left_alone_when_thresholds_are_off():
    assert quit_with(stats_with([100] * 100, failures=5)) is None


def test_failures_within_the_allowed_ratio_exit_zero():
    assert quit_with(stats_with([100] * 1000, failures=5), max_p95_ms=500, max_fail_ratio=0.01) == 0


def test_a_breach_exits_one():
    assert quit_with(stats_with([900] * 100), max_p95_ms=500, max_fail_ratio=0.01) == 1


def test_a_gated_run_with_no_requests_exits_one():
    assert quit_with(stats_with([]), max_p95_ms=500) == 1
