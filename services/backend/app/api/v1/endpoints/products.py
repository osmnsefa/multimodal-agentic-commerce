from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/products/health-db", summary="Database & pgvector extension healthcheck")
async def health_db(db: AsyncSession = Depends(get_db)):
    try:
        # Check basic database connection
        result_select_1 = await db.execute(text("SELECT 1;"))
        select_1_ok = result_select_1.scalar() == 1

        # Check pgvector extension status
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
