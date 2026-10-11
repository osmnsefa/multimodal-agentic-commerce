from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AgentQueryRequest(BaseModel):
    query: str
    user_id: str

@router.post("/agent/invoke", summary="Invoke Multi-Agent Workflow")
async def invoke_agent(payload: AgentQueryRequest):
    """
    Triggers the multi-agent orchestrator to process user intent (recommendations, support, order status).
    """
    return {
        "status": "success",
        "agent": "RecommendationAgent",
        "response": f"Agent processed query: '{payload.query}' for user '{payload.user_id}'",
        "recommended_products": ["prod-101", "prod-102"]
    }
