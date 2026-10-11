from fastapi import APIRouter, Depends, HTTPException
from app.schemas.product import MultimodalSearchRequest
from app.services.vector_search import VectorSearchService

router = APIRouter()

@router.post("/search/multimodal", summary="Multimodal Product Search")
async def multimodal_search(
    request: MultimodalSearchRequest,
    vector_service: VectorSearchService = Depends()
):
    """
    Perform multimodal hybrid search using text and/or image queries.
    """
    try:
        results = await vector_service.search_multimodal(
            text_query=request.text_query,
            image_base64=request.image_base64,
            top_k=request.top_k
        )
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
