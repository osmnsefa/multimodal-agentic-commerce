import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductOnboardingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/products/",
    response_model=ProductOnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Draft Product & Trigger Multi-Agent Pipeline",
    description="Saves product with 'draft' status and asynchronously dispatches the LangGraph onboarding pipeline via Celery worker."
)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Generate unique SKU if omitted
        sku = product_in.sku or f"AEGIS-DRAFT-{uuid.uuid4().hex[:8].upper()}"

        # 2. Check SKU uniqueness
        existing_stmt = select(Product).where(Product.sku == sku)
        existing_res = await db.execute(existing_stmt)
        if existing_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{sku}' already exists."
            )

        # 3. Create Draft Product instance
        product_id = uuid.uuid4()
        new_product = Product(
            id=product_id,
            sku=sku,
            title=product_in.title,
            description=product_in.description or "Pending agent enrichment...",
            category=product_in.category,
            price=product_in.price or 0.0,
            currency=product_in.currency or "USD",
            image_url=product_in.image_url or "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
            attributes=product_in.attributes or {},
            status="draft"
        )

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        # 4. Trigger Celery Task asynchronously
        task_id: Optional[str] = None
        try:
            from workers.tasks import run_product_agent_pipeline
            task = run_product_agent_pipeline.delay(str(new_product.id))
            task_id = task.id
            logger.info(f"Dispatched Celery task {task_id} for product {new_product.id}")
        except Exception as celery_err:
            logger.warning(f"Celery dispatch failed (running local/fallback): {celery_err}")

        return ProductOnboardingResponse(
            product_id=str(new_product.id),
            sku=new_product.sku,
            title=new_product.title,
            status=new_product.status,
            message="Product created in draft mode. Multi-agent onboarding pipeline initiated.",
            task_id=task_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create product: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product onboarding initiation failed: {str(e)}"
        )

@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Get Product Details",
    description="Retrieves a product record by ID to inspect current status and agent enrichment."
)
async def get_product_by_id(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        p_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product UUID format")

    stmt = select(Product).where(Product.id == p_uuid)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(
        id=str(product.id),
        sku=product.sku,
        title=product.title,
        description=product.description,
        category=product.category,
        price=float(product.price),
        currency=product.currency,
        image_url=product.image_url,
        attributes=product.attributes or {},
        status=product.status
    )

@router.get("/products/health-db", summary="Database & pgvector extension healthcheck")
async def health_db(db: AsyncSession = Depends(get_db)):
    try:
        result_select_1 = await db.execute(text("SELECT 1;"))
        select_1_ok = result_select_1.scalar() == 1

        result_ext = await db.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"))
        ext_row = result_ext.fetchone()

        pgvector_installed = ext_row is not None
        pgvector_version = ext_row[1] if ext_row else None

        return {
            "status": "healthy" if (select_1_ok and pgvector_installed) else "unhealthy",
            "database_connected": select_1_ok,
            "pgvector_installed": pgvector_installed,
            "pgvector_version": pgvector_version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database healthcheck failed: {str(e)}")
