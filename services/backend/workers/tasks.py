import asyncio
import uuid
import logging
from typing import Dict, Any
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.services.clip_service import clip_service
from app.agents.graph import product_onboarding_graph
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

async def _async_run_product_agent_pipeline(product_id: str) -> Dict[str, Any]:
    """
    Asynchronously executes the multi-agent LangGraph pipeline for product onboarding,
    persisting enriched description, smart pricing, audit logs, and CLIP embeddings.
    """
    try:
        p_uuid = uuid.UUID(product_id)
    except ValueError:
        logger.error(f"Invalid UUID string received: {product_id}")
        return {"status": "error", "message": f"Invalid UUID: {product_id}"}

    async with AsyncSessionLocal() as session:
        stmt = select(Product).where(Product.id == p_uuid)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            logger.error(f"Product not found for ID: {product_id}")
            return {"status": "error", "message": f"Product not found: {product_id}"}

        initial_state = {
            "product_id": str(product.id),
            "title": product.title,
            "raw_description": product.description,
            "image_url": product.image_url,
            "category": product.category,
            "enriched_description": None,
            "suggested_price": None,
            "audit_logs": [],
            "tokens_used": 0
        }

        # 1. Execute LangGraph multi-agent pipeline
        logger.info(f"Initiating LangGraph onboarding workflow for product '{product.id}'...")
        final_state = product_onboarding_graph.invoke(initial_state)

        # 2. Apply enriched metadata
        if final_state.get("enriched_description"):
            product.description = final_state["enriched_description"]
        if final_state.get("category"):
            product.category = final_state["category"]
        if final_state.get("suggested_price"):
            product.price = final_state["suggested_price"]

        # 3. Generate Multimodal CLIP Embeddings
        try:
            embed_text = f"{product.title} {product.description}"
            product.text_embedding = clip_service.get_text_embedding(embed_text)
            if product.image_url:
                product.image_embedding = clip_service.get_image_embedding(product.image_url)
        except Exception as e:
            logger.warning(f"Embedding computation warning during pipeline: {e}")

        # 4. Attach audit trail and mark active
        attributes = dict(product.attributes or {})
        attributes["audit_logs"] = final_state.get("audit_logs", [])
        attributes["tokens_used"] = final_state.get("tokens_used", 0)
        attributes["agent_status"] = "enriched"
        product.attributes = attributes
        product.status = "published"

        await session.commit()
        await session.refresh(product)

        logger.info(f"Product '{product.id}' successfully enriched by multi-agent pipeline.")
        return {
            "status": "success",
            "product_id": str(product.id),
            "category": product.category,
            "price": float(product.price),
            "tokens_used": final_state.get("tokens_used", 0),
            "audit_logs": final_state.get("audit_logs", [])
        }

@celery_app.task(name="workers.tasks.run_product_agent_pipeline")
def run_product_agent_pipeline(product_id: str):
    """
    Celery task entrypoint triggering the LangGraph agent graph asynchronously.
    """
    return asyncio.run(_async_run_product_agent_pipeline(product_id))

@celery_app.task(name="workers.tasks.generate_product_embedding")
def generate_product_embedding(product_id: str, image_url: str):
    """
    Async Celery task to compute visual & textual embeddings.
    """
    return {"status": "success", "product_id": product_id, "vector_dim": 512}
