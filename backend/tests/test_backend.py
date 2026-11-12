import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from app.db_base import Base
from app.db_session import get_db
from app.main import app
from app.models import Color,InventoryBalance,Product,ProductVariant,Role,Size,User
from app.schemas import MovementCreate
from app.inventory import register_movement
@pytest.fixture()
def db():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    Base.metadata.create_all(engine); session=sessionmaker(bind=engine,expire_on_commit=False)()
    yield session
    session.close(); Base.metadata.drop_all(engine); engine.dispose()
@pytest.fixture()
def client(db):
    def override(): yield db
    app.dependency_overrides[get_db]=override
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()
def test_health(client):
    r=client.get("/health"); assert r.status_code==200 and r.json()["status"]=="ok"
def test_products_and_duplicate_reference(client):
    p={"name":"Camiseta","model_reference":"CAM-001"}
    assert client.post("/api/v1/products",json=p).status_code==201
    assert client.get("/api/v1/products").json()[0]["name"]=="Camiseta"
    assert client.post("/api/v1/products",json=p).status_code==409
def test_variant_initializes_balance(client,db):
    p,s,c=Product(name="Pantalón",model_reference="PAN-01"),Size(name="M"),Color(name="Negro",hex_code="#000000")
    db.add_all([p,s,c]); db.commit()
    r=client.post(f"/api/v1/products/{p.id}/variants",json={"size_id":str(s.id),"color_id":str(c.id),"sku":"PAN-M-NEG","minimum_quantity":2})
    assert r.status_code==201
    stock=client.get(f"/api/v1/variants/{r.json()['id']}/stock").json()
    assert stock["quantity"]==0 and stock["minimum_quantity"]==2
def test_movement_route_closed_until_auth(client):
    assert client.post("/api/v1/inventory/movements",json={}).status_code==501
def test_movement_service_and_rollback(db):
    role=Role(name="operator"); db.add(role); db.flush()
    user=User(role_id=role.id,email="op@example.com",password_hash="test-only",full_name="Operator")
    p,s,c=Product(name="Camisa",model_reference="CAM-02"),Size(name="L"),Color(name="Azul",hex_code="#0000FF")
    db.add_all([user,p,s,c]); db.flush()
    v=ProductVariant(product_id=p.id,size_id=s.id,color_id=c.id,sku="CAM-L-AZU"); db.add(v); db.flush()
    b=InventoryBalance(variant_id=v.id,quantity=0); db.add(b); db.commit()
    incoming=MovementCreate(variant_id=v.id,movement_type="IN",quantity=8,reason="Compra",user_id=user.id)
    first=register_movement(db,incoming,"in-001")
    outgoing=MovementCreate(variant_id=v.id,movement_type="OUT",quantity=3,reason="Venta",user_id=user.id)
    second=register_movement(db,outgoing,"out-001")
    assert (first.stock_before,first.stock_after)==(0,8)
    assert (second.stock_before,second.stock_after)==(8,5) and db.get(InventoryBalance,b.id).quantity==5
    with pytest.raises(HTTPException):
        register_movement(db,MovementCreate(variant_id=v.id,movement_type="OUT",quantity=99,reason="Venta",user_id=user.id))
    assert db.get(InventoryBalance,b.id).quantity==5
