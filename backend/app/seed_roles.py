from sqlalchemy import select
from app.db_session import get_session_factory
from app.models import Role

DEFAULT_ROLES = {
    "ADMIN": "Administración total del sistema",
    "MANAGER": "Gestión de catálogo e inventario",
    "STAFF": "Operaciones habituales de inventario",
}

def seed_roles() -> None:
    db = get_session_factory()()
    try:
        for name, description in DEFAULT_ROLES.items():
            role = db.scalar(select(Role).where(Role.name == name))
            if role is None:
                db.add(Role(name=name, description=description))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()
