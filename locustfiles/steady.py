"""Steady load: one user class shared by every scenario, plus optional pass/fail thresholds."""

import logging
import random
from argparse import ArgumentParser, Namespace
from typing import cast

from locust import HttpUser, between, events, tag, task
from locust.env import Environment
from locust.stats import StatsEntry


class ApiUser(HttpUser):
    wait_time = between(1, 3)

    @task(6)
    def list_users(self) -> None:
        self.client.get("/users")

    @task(3)
    def get_user(self) -> None:
        # The target app seeds users 1-5 and never evicts them
        self.client.get(f"/users/{random.randint(1, 5)}", name="/users/[id]")

    @task(2)
    def create_user(self) -> None:
        suffix = random.randint(1000, 9999)
        payload = {"name": f"LoadUser {suffix}", "email": f"load.{suffix}@example.com"}
        self.client.post("/users", json=payload, name="/users [create]")

    @tag("negative")
    @task(1)
    def get_missing_user(self) -> None:
        # IDs start at 1, so 0 never exists
        with self.client.get("/users/0", name="/users/[missing]", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
            else:
                response.failure(f"expected 404, got {response.status_code}")

    @tag("negative")
    @task(1)
    def create_invalid_user(self) -> None:
        payload = {"email": "no-name@example.com"}
        with self.client.post("/users", json=payload, name="/users [invalid]", catch_response=True) as response:
            if response.status_code == 400:
                response.success()
            else:
                response.failure(f"expected 400, got {response.status_code}")


@events.init_command_line_parser.add_listener
def add_threshold_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--max-p95-ms", type=float, default=0, help="Exit 1 if the overall p95 is above this many ms (0 disables)"
    )
    parser.add_argument(
        "--max-fail-ratio", type=float, default=1, help="Exit 1 if the failed share is above this (1 disables)"
    )


def threshold_breaches(total: StatsEntry, max_p95_ms: float, max_fail_ratio: float) -> list[str]:
    """Return one message per breached threshold. `total` is Locust's aggregated StatsEntry."""
    if total.num_requests == 0:
        return ["no requests were made"]

    breaches = []
    p95 = total.get_response_time_percentile(0.95)
    if max_p95_ms and p95 > max_p95_ms:
        breaches.append(f"p95 {p95:.0f} ms is above {max_p95_ms:.0f} ms")
    if total.fail_ratio > max_fail_ratio:
        breaches.append(f"failure ratio {total.fail_ratio:.1%} is above {max_fail_ratio:.1%}")
    return breaches


@events.quitting.add_listener
def apply_thresholds(environment: Environment, **kwargs: object) -> None:
    options = cast(Namespace, environment.parsed_options)
    if not options.max_p95_ms and options.max_fail_ratio >= 1:
        return  # thresholds are off, so Locust keeps its default exit code

    breaches = threshold_breaches(environment.stats.total, options.max_p95_ms, options.max_fail_ratio)
    for breach in breaches:
        logging.error("Threshold breached: %s", breach)
    # Locust exits 1 on any failed request by default; with thresholds on, they decide instead
    environment.process_exit_code = 1 if breaches else 0
