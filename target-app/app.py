import itertools
import random
import threading
import time
from datetime import datetime, timezone
from typing import TypedDict

from flask import Flask, Response, g, jsonify, request
from flask.typing import ResponseReturnValue
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, Histogram, generate_latest
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

SEED_NAMES = ["Alice", "Bob", "Charlie", "David", "Eve"]
MAX_USERS = 1000
UNMEASURED_PATHS = {"/metrics", "/health"}

REQUEST_DURATION = Histogram(
    "app_http_request_duration_seconds",
    "Time spent handling a request, by method, route and status.",
    ["method", "route", "status"],
    buckets=(0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, 2.5),
)
IN_FLIGHT = Gauge("app_http_requests_in_flight", "Requests currently being handled.")


class User(TypedDict):
    id: int
    name: str
    email: str
    created_at: str


users: dict[int, User] = {}
user_ids = itertools.count(1)
users_lock = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_user(name: str, email: str) -> User:
    with users_lock:
        user: User = {"id": next(user_ids), "name": name, "email": email, "created_at": now()}
        users[user["id"]] = user
        if len(users) > MAX_USERS:
            # dicts keep insertion order, so this is the oldest user that is not a seed
            del users[next(user_id for user_id in users if user_id > len(SEED_NAMES))]
    return user


for seed_name in SEED_NAMES:
    add_user(seed_name, f"{seed_name.lower()}@example.com")


def simulate_work(low: float, high: float) -> None:
    time.sleep(random.uniform(low, high))


@app.before_request
def start_timer() -> None:
    if request.path not in UNMEASURED_PATHS:
        g.started = time.perf_counter()
        IN_FLIGHT.inc()


@app.after_request
def record_request(response: Response) -> Response:
    started = g.pop("started", None)
    if started is not None:
        IN_FLIGHT.dec()
        route = request.url_rule.rule if request.url_rule else "unmatched"
        REQUEST_DURATION.labels(request.method, route, response.status_code).observe(time.perf_counter() - started)
    return response


@app.errorhandler(404)
def not_found(error: HTTPException) -> ResponseReturnValue:
    return jsonify({"error": "Resource not found"}), 404


@app.route("/")
def index() -> ResponseReturnValue:
    return jsonify({"message": "Load test target API", "endpoints": ["/users", "/users/<id>", "/health", "/metrics"]})


@app.route("/health")
def health() -> ResponseReturnValue:
    return jsonify({"status": "healthy"})


@app.route("/metrics")
def metrics() -> ResponseReturnValue:
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/users", methods=["GET"])
def list_users() -> ResponseReturnValue:
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if page < 1 or not 1 <= per_page <= 100:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    simulate_work(0.05, 0.1)
    with users_lock:
        all_users = list(users.values())
    start = (page - 1) * per_page
    return jsonify(
        {"users": all_users[start : start + per_page], "page": page, "per_page": per_page, "total": len(all_users)}
    )


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int) -> ResponseReturnValue:
    simulate_work(0.05, 0.2)
    user = users.get(user_id)
    if user is None:
        return jsonify({"error": f"User {user_id} not found"}), 404
    return jsonify({"user": user})


@app.route("/users", methods=["POST"])
def create_user() -> ResponseReturnValue:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    name = body.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "'name' must be a non-empty string"}), 400

    email = body.get("email", "")
    if not isinstance(email, str) or (email and "@" not in email):
        return jsonify({"error": "'email' must be a string containing '@'"}), 400

    simulate_work(0.1, 0.3)
    return jsonify({"user": add_user(name.strip(), email)}), 201
