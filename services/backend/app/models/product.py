import uuid
from sqlalchemy import Column, String, Text, Numeric, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), index=True, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    image_url = Column(Text, nullable=False)
    attributes = Column(JSONB, default=dict, nullable=False)
    image_embedding = Column(Vector(512), nullable=True)
    text_embedding = Column(Vector(512), nullable=True)
    status = Column(String(20), default="draft", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
