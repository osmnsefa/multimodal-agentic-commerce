import logging
from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes import cataloger_node, pricing_node, audit_node

logger = logging.getLogger(__name__)

def build_product_onboarding_graph():
    """
    Constructs and compiles the multi-agent product onboarding pipeline.
    Flow: START -> cataloger_node -> pricing_node -> audit_node -> END
    """
    workflow = StateGraph(AgentState)

    # 1. Register agent nodes
    workflow.add_node("cataloger_node", cataloger_node)
    workflow.add_node("pricing_node", pricing_node)
    workflow.add_node("audit_node", audit_node)

    # 2. Define sequential execution flow
    workflow.add_edge(START, "cataloger_node")
    workflow.add_edge("cataloger_node", "pricing_node")
    workflow.add_edge("pricing_node", "audit_node")
    workflow.add_edge("audit_node", END)

    # 3. Compile graph into runnable pipeline
    app_graph = workflow.compile()
    logger.info("Compiled product_onboarding_graph successfully.")
    return app_graph

product_onboarding_graph = build_product_onboarding_graph()
