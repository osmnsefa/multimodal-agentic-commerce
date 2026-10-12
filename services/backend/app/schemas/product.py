from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class ProductBase(BaseModel):
    sku: Optional[str] = Field(None, json_schema_extra={"example": "AEGIS-TECH-001"})
    title: str = Field(..., json_schema_extra={"example": "Wireless Noise-Canceling Headphones"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "High-fidelity audio with active noise cancellation."})
    price: Optional[float] = Field(default=0.0, json_schema_extra={"example": 299.99})
    currency: str = Field(default="USD", json_schema_extra={"example": "USD"})
    category: Optional[str] = Field(None, json_schema_extra={"example": "Electronics"})
    image_url: Optional[str] = Field(default="https://images.unsplash.com/photo-1523275335684-37898b6baf30", json_schema_extra={"example": "https://example.com/images/headphones.jpg"})
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProductCreate(ProductBase):
    sku: Optional[str] = None
    title: str
    description: str = Field(default="", json_schema_extra={"example": "Initial draft description"})

class ProductResponse(ProductBase):
    id: str
    status: str = "draft"

    model_config = ConfigDict(from_attributes=True)

class ProductOnboardingResponse(BaseModel):
    product_id: str
    sku: str
    title: str
    status: str
    message: str
    task_id: Optional[str] = None

class ProductSearchResultItem(BaseModel):
    id: str
    sku: str
    title: str
    description: str
    category: Optional[str] = None
    price: float
    currency: str = "USD"
    image_url: str
    attributes: Dict[str, Any] = {}
    similarity_score: float
    distance: float
    text_distance: Optional[float] = None
    image_distance: Optional[float] = None

class SearchResponse(BaseModel):
    query_type: str
    total: int
    alpha: Optional[float] = None
    results: List[ProductSearchResultItem]

class MultimodalSearchRequest(BaseModel):
    text_query: Optional[str] = Field(None, json_schema_extra={"example": "Red running shoes"})
    image_base64: Optional[str] = Field(None, json_schema_extra={"example": "data:image/png;base64,..."})
    top_k: int = Field(default=10, ge=1, le=100)
