import operator
from typing import TypedDict, Optional, List, Dict, Any, Annotated

class AgentState(TypedDict):
    """
    State definition for the LangGraph product onboarding multi-agent workflow.
    """
    product_id: str
    title: str
    raw_description: str
    image_url: str
    category: Optional[str]
    enriched_description: Optional[str]
    suggested_price: Optional[float]
    audit_logs: Annotated[List[Dict[str, Any]], operator.add]
    tokens_used: int
