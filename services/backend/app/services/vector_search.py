from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.services.clip_service import clip_service

async def search_by_image(
    db: AsyncSession,
    query_image_bytes: bytes,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Extracts query image embedding and executes nearest neighbor cosine distance search
    against pgvector HNSW index on `products.image_embedding`.
    """
    image_emb = clip_service.get_image_embedding(query_image_bytes)
    distance_col = Product.image_embedding.cosine_distance(image_emb).label("distance")

    stmt = (
        select(Product, distance_col)
        .where(Product.image_embedding.isnot(None))
        .order_by(distance_col.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    products = []
    for product, dist in rows:
        dist_val = float(dist) if dist is not None else 1.0
        similarity = round(max(0.0, 1.0 - dist_val), 4)
        products.append({
            "id": str(product.id),
            "sku": product.sku,
            "title": product.title,
            "description": product.description,
            "category": product.category,
            "price": float(product.price),
            "currency": product.currency,
            "image_url": product.image_url,
            "attributes": product.attributes or {},
            "similarity_score": similarity,
            "distance": round(dist_val, 4)
        })
    return products

async def search_hybrid(
    db: AsyncSession,
    query_text: str,
    query_image_bytes: Optional[bytes] = None,
    alpha: float = 0.5,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Executes hybrid search blending semantic textual embeddings with visual embeddings
    using the alpha weighting parameter: alpha * text_dist + (1 - alpha) * image_dist.
    """
    text_emb = clip_service.get_text_embedding(query_text)
    text_dist = Product.text_embedding.cosine_distance(text_emb).label("text_dist")

    if query_image_bytes:
        image_emb = clip_service.get_image_embedding(query_image_bytes)
        image_dist = Product.image_embedding.cosine_distance(image_emb).label("image_dist")
        combined_dist = (alpha * text_dist + (1.0 - alpha) * image_dist).label("combined_dist")

        stmt = (
            select(Product, text_dist, image_dist, combined_dist)
            .where(Product.text_embedding.isnot(None))
            .where(Product.image_embedding.isnot(None))
            .order_by(combined_dist.asc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        products = []
        for product, t_dist, i_dist, c_dist in rows:
            c_dist_val = float(c_dist) if c_dist is not None else 1.0
            similarity = round(max(0.0, 1.0 - c_dist_val), 4)
            products.append({
                "id": str(product.id),
                "sku": product.sku,
                "title": product.title,
                "description": product.description,
                "category": product.category,
                "price": float(product.price),
                "currency": product.currency,
                "image_url": product.image_url,
                "attributes": product.attributes or {},
                "similarity_score": similarity,
                "distance": round(c_dist_val, 4),
                "text_distance": round(float(t_dist), 4) if t_dist is not None else None,
                "image_distance": round(float(i_dist), 4) if i_dist is not None else None
            })
        return products
    else:
        stmt = (
            select(Product, text_dist)
            .where(Product.text_embedding.isnot(None))
            .order_by(text_dist.asc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        products = []
        for product, t_dist_val in rows:
            dist_val = float(t_dist_val) if t_dist_val is not None else 1.0
            similarity = round(max(0.0, 1.0 - dist_val), 4)
            products.append({
                "id": str(product.id),
                "sku": product.sku,
                "title": product.title,
                "description": product.description,
                "category": product.category,
                "price": float(product.price),
                "currency": product.currency,
                "image_url": product.image_url,
                "attributes": product.attributes or {},
                "similarity_score": similarity,
                "distance": round(dist_val, 4)
            })
        return products

class VectorSearchService:
    """Class wrapper for dependency injection or service container."""
    search_by_image = staticmethod(search_by_image)
    search_hybrid = staticmethod(search_hybrid)
