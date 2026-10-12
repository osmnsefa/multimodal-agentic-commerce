import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.agents.state import AgentState
from app.agents.nodes import cataloger_node, pricing_node, audit_node
from app.agents.graph import product_onboarding_graph
from workers.tasks import _async_run_product_agent_pipeline

client = TestClient(app)

def test_cataloger_node_enrichment():
    """Test cataloger node categorization and SEO description generation."""
    state: AgentState = {
        "product_id": "test-123",
        "title": "Aegis Pro Active Noise Canceling Wireless Headphones",
        "raw_description": "Wireless headphones with ANC and long battery life.",
        "image_url": "https://example.com/headphones.jpg",
        "category": None,
        "enriched_description": None,
        "suggested_price": None,
        "audit_logs": [],
        "tokens_used": 0
    }

    result = cataloger_node(state)
    assert result["category"] == "Electronics"
    assert "Aegis Pro Active Noise Canceling" in result["enriched_description"]
    assert "Aegis AI Cataloger" in result["enriched_description"]
    assert len(result["audit_logs"]) == 1
    assert result["audit_logs"][0]["node"] == "cataloger_node"
    assert result["tokens_used"] > 0

def test_pricing_node_evaluation():
    """Test pricing node calculates price and attaches audit trail."""
    state: AgentState = {
        "product_id": "test-123",
        "title": "Aegis Pro Noise-Canceling Titanium Headphones",
        "raw_description": "Premium titanium headphones with active ANC",
        "image_url": "https://example.com/headphones.jpg",
        "category": "Electronics",
        "enriched_description": "Enriched description...",
        "suggested_price": None,
        "audit_logs": [],
        "tokens_used": 150
    }

    result = pricing_node(state)
    assert result["suggested_price"] is not None
    assert result["suggested_price"] > 100.0  # Electronics benchmark with multipliers
    assert len(result["audit_logs"]) == 1
    assert result["audit_logs"][0]["node"] == "pricing_node"
    assert result["tokens_used"] > 150

def test_audit_node_consolidation():
    """Test audit node compiles final metrics and passes approval."""
    state: AgentState = {
        "product_id": "test-123",
        "title": "Sample Product",
        "raw_description": "Sample desc",
        "image_url": "https://example.com/sample.jpg",
        "category": "Electronics",
        "enriched_description": "Enriched",
        "suggested_price": 249.99,
        "audit_logs": [{"node": "cataloger_node"}, {"node": "pricing_node"}],
        "tokens_used": 300
    }

    result = audit_node(state)
    assert len(result["audit_logs"]) == 1
    assert result["audit_logs"][0]["details"]["status"] == "APPROVED"
    assert result["tokens_used"] > 300

def test_full_langgraph_workflow_invoke():
    """Test end-to-end execution of the LangGraph state graph."""
    initial_state: AgentState = {
        "product_id": "prod-e2e-001",
        "title": "Waterproof Trail Running Carbon Fiber Shoes",
        "raw_description": "High performance mountain running shoes with Vibram grip.",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "category": None,
        "enriched_description": None,
        "suggested_price": None,
        "audit_logs": [],
        "tokens_used": 0
    }

    final_state = product_onboarding_graph.invoke(initial_state)

    assert final_state["category"] == "Sports & Outdoors"
    assert final_state["enriched_description"] is not None
    assert final_state["suggested_price"] is not None
    assert final_state["suggested_price"] > 100.0
    assert len(final_state["audit_logs"]) == 3
    assert final_state["tokens_used"] > 0

def test_post_product_onboarding_endpoint():
    """Test POST /api/v1/products/ creating draft product and returning task status."""
    payload = {
        "title": "Smart Robot Vacuum Cleaner with LiDAR Laser",
        "description": "Autonomous robotic vacuum with laser navigation.",
        "category": "Home & Living",
        "image_url": "https://images.unsplash.com/photo-1518640467707-6811f4a6ab73"
    }

    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "product_id" in data
    assert data["status"] == "draft"
    assert "Multi-agent onboarding pipeline initiated" in data["message"]

    # Verify product is retrievable
    prod_res = client.get(f"/api/v1/products/{data['product_id']}")
    assert prod_res.status_code == 200
    assert prod_res.json()["title"] == payload["title"]

def test_async_product_agent_pipeline_execution():
    """Test that _async_run_product_agent_pipeline enriches the product in PostgreSQL."""
    import asyncio
    # 1. Create a draft product first
    payload = {
        "title": "Japanese Selvedge Denim Cotton Jacket",
        "description": "Raw unwashed indigo denim jacket with selvedge id.",
        "image_url": "https://images.unsplash.com/photo-1542272604-780c96856592"
    }
    create_res = client.post("/api/v1/products/", json=payload)
    assert create_res.status_code == 201
    prod_id = create_res.json()["product_id"]

    # 2. Execute pipeline directly
    result = asyncio.run(_async_run_product_agent_pipeline(prod_id))
    assert result["status"] == "success"
    assert result["product_id"] == prod_id
    assert result["category"] == "Clothing"
    assert result["price"] > 0

    # 3. Fetch product from API and verify enriched status
    get_res = client.get(f"/api/v1/products/{prod_id}")
    assert get_res.status_code == 200
    pdata = get_res.json()
    assert pdata["status"] == "published"
    assert "Aegis AI Cataloger" in pdata["description"]
    assert pdata["attributes"]["agent_status"] == "enriched"
    assert len(pdata["attributes"]["audit_logs"]) == 3
