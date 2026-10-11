from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class ProductBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Wireless Noise-Canceling Headphones"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "High-fidelity audio with active noise cancellation."})
    price: float = Field(..., json_schema_extra={"example": 299.99})
    category: str = Field(..., json_schema_extra={"example": "Electronics"})
    image_url: Optional[str] = Field(None, json_schema_extra={"example": "https://example.com/images/headphones.jpg"})

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

class MultimodalSearchRequest(BaseModel):
    text_query: Optional[str] = Field(None, json_schema_extra={"example": "Red running shoes"})
    image_base64: Optional[str] = Field(None, json_schema_extra={"example": "data:image/png;base64,..."})
    top_k: int = Field(default=10, ge=1, le=100)
