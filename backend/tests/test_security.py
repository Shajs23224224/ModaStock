from app.security import create_access_token, hash_password, verify_password
import jwt
from app.core_config import get_settings

def test_password_hash_is_not_plaintext_and_verifies():
    hashed = hash_password("ModaStock-Segura-2026!")
    assert hashed != "ModaStock-Segura-2026!"
    assert verify_password("ModaStock-Segura-2026!", hashed)
    assert not verify_password("incorrecta", hashed)

def test_jwt_contains_subject_role_and_expiration():
    token = create_access_token("00000000-0000-0000-0000-000000000001", "STAFF")
    payload = jwt.decode(token, get_settings().jwt_secret_key, algorithms=["HS256"])
    assert payload["sub"] == "00000000-0000-0000-0000-000000000001"
    assert payload["role"] == "STAFF"
    assert "exp" in payload
