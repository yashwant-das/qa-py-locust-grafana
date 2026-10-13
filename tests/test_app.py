import pytest
from prometheus_client import REGISTRY

import app as target


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(target, "simulate_work", lambda low, high: None)
    return target.app.test_client()


def request_count(method, route, status):
    labels = {"method": method, "route": route, "status": status}
    return REGISTRY.get_sample_value("app_http_request_duration_seconds_count", labels) or 0


def test_lists_seed_users(client):
    body = client.get("/users?per_page=5").get_json()
    assert [user["name"] for user in body["users"]] == target.SEED_NAMES


def test_rejects_bad_pagination(client):
    assert client.get("/users?per_page=0").status_code == 400
    assert client.get("/users?page=0").status_code == 400


def test_missing_user_is_404(client):
    assert client.get("/users/0").status_code == 404


def test_creates_user(client):
    response = client.post("/users", json={"name": "  Grace  ", "email": "grace@example.com"})
    assert response.status_code == 201
    created = response.get_json()["user"]
    assert created["name"] == "Grace"
    assert client.get(f"/users/{created['id']}").get_json()["user"] == created


@pytest.mark.parametrize(
    "payload",
    [{}, {"name": ""}, {"name": 42}, {"name": "Grace", "email": "not-an-email"}, {"name": "Grace", "email": 7}, ["Grace"], "Grace"],
)
def test_rejects_invalid_user(client, payload):
    assert client.post("/users", json=payload).status_code == 400


def test_rejects_non_json_body(client):
    assert client.post("/users", data="name=Grace").status_code == 400


def test_user_store_is_capped_and_keeps_seeds(client, monkeypatch):
    monkeypatch.setattr(target, "MAX_USERS", len(target.users) + 2)
    created = [client.post("/users", json={"name": f"Cap {i}"}).get_json()["user"]["id"] for i in range(4)]
    assert len(target.users) == target.MAX_USERS
    assert created[-1] in target.users
    assert all(seed_id in target.users for seed_id in range(1, len(target.SEED_NAMES) + 1))


def test_metrics_count_requests_by_route_and_status(client):
    found_before = request_count("GET", "/users/<int:user_id>", "200")
    missing_before = request_count("GET", "/users/<int:user_id>", "404")
    client.get("/users/1")
    client.get("/users/0")
    assert request_count("GET", "/users/<int:user_id>", "200") == found_before + 1
    assert request_count("GET", "/users/<int:user_id>", "404") == missing_before + 1


def test_unknown_paths_share_one_route_label(client):
    before = request_count("GET", "unmatched", "404")
    client.get("/nope/1")
    client.get("/nope/2")
    assert request_count("GET", "unmatched", "404") == before + 2


def test_metrics_and_health_are_not_measured(client):
    client.get("/health")
    exposition = client.get("/metrics").get_data(as_text=True)
    assert "app_http_request_duration_seconds_bucket" in exposition
    assert 'route="/metrics"' not in exposition
    assert 'route="/health"' not in exposition
    assert "app_http_requests_in_flight 0.0" in exposition
