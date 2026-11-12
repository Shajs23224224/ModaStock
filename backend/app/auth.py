import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core_config import get_settings
from app.db_session import get_db
from app.models import Role, User
from app.schemas import LoginRequest, RegisterRequest, TokenRead, UserRead
from app.security import create_access_token, hash_password, verify_password
import jwt

router = APIRouter(prefix="/auth", tags=["Autenticación"])
bearer = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Autenticación requerida", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret_key, algorithms=["HS256"])
        user_id = uuid.UUID(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"}) from None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario inexistente o inactivo")
    return user

def require_roles(*allowed: str):
    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        role = db.get(Role, user.role_id)
        if role is None or role.name not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para esta operación")
        return user
    return dependency

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    role = db.scalar(select(Role).where(Role.name == "STAFF"))
    if role is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Roles no inicializados; ejecuta el seed de roles")
    user = User(role_id=role.id, email=str(payload.email).lower(), full_name=payload.full_name.strip(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese correo") from None
    db.refresh(user)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name, role=role.name, is_active=user.is_active)

@router.post("/login", response_model=TokenRead)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos", headers={"WWW-Authenticate": "Bearer"})
    role = db.get(Role, user.role_id)
    if role is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "La cuenta no tiene un rol válido")
    token = create_access_token(str(user.id), role.name)
    return TokenRead(access_token=token, expires_in=get_settings().access_token_expire_minutes * 60)

@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = db.get(Role, user.role_id)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name, role=role.name if role else "UNKNOWN", is_active=user.is_active)
