import pytest

from app import app, reset_tickets


@pytest.fixture
def client():
    reset_tickets()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_list_tickets_returns_200(client):
    response = client.get("/api/tickets")
    assert response.status_code == 200
    assert len(response.get_json()) == 5


def test_get_ticket_1_has_a_title(client):
    response = client.get("/api/tickets/1")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Laptop not charging"


def test_unknown_ticket_returns_404(client):
    response = client.get("/api/tickets/9999")
    assert response.status_code == 404



# Bug 1: Priority sorting
def test_tickets_sorted_by_priority(client):
    response = client.get("/api/tickets")
    priorities = [ticket["priority"] for ticket in response.get_json()]

    assert priorities == ["High", "High", "Medium", "Medium", "Low"]


# Bug 2: Empty title validation
def test_empty_title_returns_400(client):
    response = client.post("/api/tickets", json={
        "title": "",
        "description": "Testing",
        "category": "Hardware",
        "priority": "High"
    })

    assert response.status_code == 400


# Bug 3: Correct status displayed on screen
def test_resolved_ticket_displays_correct_status(client):
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "Excel keeps crashing on startup" in html
    assert '<span class="badge">Resolved</span>' in html


# Negative Test 1: Missing title
def test_missing_title_returns_400(client):
    response = client.post("/api/tickets", json={
        "category": "Hardware",
        "priority": "High"
    })

    assert response.status_code == 400


# Negative Test 2: Invalid category
def test_unknown_category_returns_400(client):
    response = client.post("/api/tickets", json={
        "title": "Printer issue",
        "category": "Furniture",
        "priority": "High"
    })

    assert response.status_code == 400


# Negative Test 3: Invalid priority
def test_unknown_priority_returns_400(client):
    response = client.post("/api/tickets", json={
        "title": "Printer issue",
        "category": "Hardware",
        "priority": "Urgent"
    })

    assert response.status_code == 400


# Negative Test 4: Invalid status
def test_invalid_status_returns_400(client):
    response = client.patch("/api/tickets/1/status", json={
        "status": "Pending"
    })

    assert response.status_code == 400


# Negative Test 5: Update unknown ticket
def test_unknown_ticket_status_update_returns_404(client):
    response = client.patch("/api/tickets/9999/status", json={
        "status": "Resolved"
    })

    assert response.status_code == 404
