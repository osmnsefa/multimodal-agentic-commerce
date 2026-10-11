import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base

class AgentAuditLog(Base):
    __tablename__ = "agent_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    agent_name = Column(String(50), nullable=False)
    input_payload = Column(JSONB, nullable=True)
    output_payload = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
