"""Initial pgvector tables and HNSW indexes

Revision ID: 0001_initial_pgvector
Revises: 
Create Date: 2026-10-09 19:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0001_initial_pgvector'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), server_default='USD', nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('attributes', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('image_embedding', Vector(512), nullable=True),
        sa.Column('text_embedding', Vector(512), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    op.create_index('ix_products_category', 'products', ['category'], unique=False)

    # 3. Create agent_audit_logs table
    op.create_table(
        'agent_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=True),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('input_payload', postgresql.JSONB(), nullable=True),
        sa.Column('output_payload', postgresql.JSONB(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # 4. Create HNSW cosine vector indexes for image_embedding and text_embedding
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_image_embedding_hnsw "
        "ON products USING hnsw (image_embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_text_embedding_hnsw "
        "ON products USING hnsw (text_embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_products_text_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS idx_products_image_embedding_hnsw;")
    op.drop_table('agent_audit_logs')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_table('products')
