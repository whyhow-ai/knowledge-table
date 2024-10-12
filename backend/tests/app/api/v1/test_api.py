"""Tests for the main API router configuration."""

from fastapi.testclient import TestClient

from app.api.v1.api import api_router
from app.main import app  # Assuming your main FastAPI app is in app/main.py


def test_api_router_configuration():
    """Test that the API router is configured correctly."""
    # GIVEN: The main FastAPI application with the API router included

    # WHEN: We inspect the routes of the API router
    routes = api_router.routes

    # THEN: The router should have the correct number of routes
    assert len(routes) == 4  # Update this number if it changes again

    # AND: Each route should have the correct path and methods
    expected_routes = [
        ("/document", ["POST"]),
        ("/document/{document_id}", ["DELETE"]),
        ("/graph/export-triples", ["POST"]),
        ("/query", ["POST"]),
    ]

    for route, (expected_path, expected_methods) in zip(
        routes, expected_routes
    ):
        assert route.path == expected_path
        assert set(route.methods) == set(expected_methods)


def test_api_endpoints_accessibility():
    """Test that the API endpoints are accessible."""
    # GIVEN: A test client for our FastAPI application
    client = TestClient(app)

    # WHEN: We make requests to each endpoint
    responses = [
        client.post("/api/v1/document"),
        client.post("/api/v1/graph/export-triples"),
        client.post("/api/v1/query"),
    ]

    # THEN: Each response should not be a 404 (Not Found) error
    for response in responses:
        assert (
            response.status_code != 404
        ), f"Endpoint not found: {response.url}"

    # Note: The actual status codes might be 200, 400, 401, 403, etc., depending on your implementation
    # The important thing is that the endpoints exist and are not 404
