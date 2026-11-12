from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core_config import get_settings
from app.catalog import router as catalog_router
settings=get_settings()
app=FastAPI(title=settings.app_name,version="0.1.0",description="API REST ModaStock")
@app.get("/health",tags=["Salud"])
def health(): return {"status":"ok","service":"modastock-api"}
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["Authorization","Content-Type","Idempotency-Key"])
app.include_router(catalog_router,prefix=settings.api_v1_prefix)
@app.post("/api/v1/inventory/movements",status_code=501,tags=["Inventario"])
def movement_requires_authentication():
    raise HTTPException(501,"Escritura deshabilitada hasta implementar autenticación y autorización en Fase 5")
