from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import require_roles, router as auth_router
from app.catalog import router as catalog_router
from app.core_config import get_settings
from app.db_session import get_db
from app.inventory import register_movement
from app.models import User
from app.schemas import MovementCreate

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="API REST ModaStock",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)


@app.get("/health", tags=["Salud"])
def health():
    """Liveness probe: confirma que el proceso de API está activo."""
    return {"status": "ok", "service": "modastock-api"}


@app.get("/health/ready", tags=["Salud"])
def readiness(db: Session = Depends(get_db)):
    """Readiness probe: confirma que la API puede consultar la base de datos."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        ) from None
    return {"status": "ready", "service": "modastock-api", "database": "ok"}


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(catalog_router, prefix=settings.api_v1_prefix)


@app.post("/api/v1/inventory/movements", status_code=201, tags=["Inventario"])
def create_inventory_movement(
    payload: MovementCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("STAFF", "MANAGER", "ADMIN")),
):
    return register_movement(db, payload, user.id, idempotency_key)
