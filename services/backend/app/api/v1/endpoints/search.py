import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.product import SearchResponse, MultimodalSearchRequest
from app.services.vector_search import search_by_image, search_hybrid

router = APIRouter()

@router.post(
    "/search/visual",
    response_model=SearchResponse,
    summary="Visual Similarity Search",
    description="Upload an image to find visually matching products via pgvector HNSW index."
)
async def visual_search(
    file: UploadFile = File(..., description="Query image file"),
    limit: int = Query(default=5, ge=1, le=50, description="Max products to return"),
    db: AsyncSession = Depends(get_db)
):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        results = await search_by_image(db=db, query_image_bytes=image_bytes, limit=limit)
        return SearchResponse(
            query_type="visual",
            total=len(results),
            results=results
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual search failed: {str(e)}")

@router.post(
    "/search/hybrid",
    response_model=SearchResponse,
    summary="Hybrid Multimodal Search",
    description="Search products by combining semantic text query and optional reference image with alpha weighting."
)
async def hybrid_search(
    query_text: str = Form(..., description="Text query description"),
    file: Optional[UploadFile] = File(None, description="Optional image upload"),
    alpha: float = Form(default=0.5, ge=0.0, le=1.0, description="Weighting factor: 1.0 = text only, 0.0 = image only"),
    limit: int = Form(default=5, ge=1, le=50, description="Max products to return"),
    db: AsyncSession = Depends(get_db)
):
    try:
        image_bytes = None
        if file is not None:
            content = await file.read()
            if content:
                image_bytes = content

        results = await search_hybrid(
            db=db,
            query_text=query_text,
            query_image_bytes=image_bytes,
            alpha=alpha,
            limit=limit
        )

        query_type = "hybrid" if image_bytes else "text"
        return SearchResponse(
            query_type=query_type,
            total=len(results),
            alpha=alpha,
            results=results
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")

@router.post(
    "/search/multimodal",
    response_model=SearchResponse,
    summary="JSON Multimodal Search",
    description="JSON endpoint for API/Agent clients accepting text query and/or base64 encoded image."
)
async def multimodal_search_json(
    request: MultimodalSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        image_bytes = None
        if request.image_base64:
            b64_str = request.image_base64
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            image_bytes = base64.b64decode(b64_str)

        text_query = request.text_query or ""
        if image_bytes and not text_query:
            results = await search_by_image(db=db, query_image_bytes=image_bytes, limit=request.top_k)
            query_type = "visual"
        else:
            results = await search_hybrid(
                db=db,
                query_text=text_query,
                query_image_bytes=image_bytes,
                alpha=0.5 if image_bytes else 1.0,
                limit=request.top_k
            )
            query_type = "hybrid" if image_bytes else "text"

        return SearchResponse(
            query_type=query_type,
            total=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multimodal search failed: {str(e)}")
