import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_dummy_image_bytes() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (32, 32), color="blue")
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_search_hybrid_text_only():
    """Test hybrid search with text query only (alpha=1.0 text-dominant)."""
    response = client.post(
        "/api/v1/search/hybrid",
        data={
            "query_text": "Kulaklık",
            "alpha": 1.0,
            "limit": 3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "query_type" in data
    assert data["query_type"] == "text"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["total"] >= 0
    if data["total"] > 0:
        item = data["results"][0]
        assert "id" in item
        assert "title" in item
        assert "similarity_score" in item
        assert 0.0 <= item["similarity_score"] <= 1.0

def test_search_hybrid_with_image_and_text():
    """Test hybrid search with both text query and image upload."""
    dummy_img = create_dummy_image_bytes()
    response = client.post(
        "/api/v1/search/hybrid",
        data={
            "query_text": "Ceket",
            "alpha": 0.5,
            "limit": 5
        },
        files={
            "file": ("test.png", dummy_img, "image/png")
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["alpha"] == 0.5
    if data["total"] > 0:
        item = data["results"][0]
        assert "id" in item
        assert "title" in item
        assert "price" in item
        assert "similarity_score" in item

def test_search_visual():
    """Test visual search endpoint with an uploaded image file."""
    dummy_img = create_dummy_image_bytes()
    response = client.post(
        "/api/v1/search/visual",
        files={
            "file": ("sample.png", dummy_img, "image/png")
        },
        params={"limit": 4}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert data["query_type"] == "visual"
    if data["total"] > 0:
        item = data["results"][0]
        assert "id" in item
        assert "title" in item
        assert "category" in item
        assert "similarity_score" in item

def test_search_hybrid_empty_validation():
    """Test that submitting without required query_text form field returns 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/search/hybrid",
        data={}
    )
    assert response.status_code == 422
