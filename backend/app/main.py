from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core_config import get_settings
from app.catalog import router as catalog_router
from app.auth import router as auth_router, require_roles
from app.db_session import get_db
from app.inventory import register_movement
from app.models import User
from app.schemas import MovementCreate
settings=get_settings()
app=FastAPI(title=settings.app_name,version="0.2.0",description="API REST ModaStock")
@app.get("/health",tags=["Salud"])
def health():
    return {"status":"ok","service":"modastock-api"}
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["Authorization","Content-Type","Idempotency-Key"])
app.include_router(auth_router,prefix=settings.api_v1_prefix)
app.include_router(catalog_router,prefix=settings.api_v1_prefix)
@app.post("/api/v1/inventory/movements",status_code=201,tags=["Inventario"])
def create_inventory_movement(payload:MovementCreate,idempotency_key:str|None=Header(default=None,alias="Idempotency-Key"),db:Session=Depends(get_db),user:User=Depends(require_roles("STAFF","MANAGER","ADMIN"))):
    return register_movement(db,payload,user.id,idempotency_key)
