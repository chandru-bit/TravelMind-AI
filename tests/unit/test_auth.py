import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.auth.jwt import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    raw_pass = "secure_password_123"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) == True
    assert verify_password("wrong_password", hashed) == False

def test_jwt_token_encoding_decoding():
    data = {"sub": "user-uuid-12345", "email": "test@travelmind.ai"}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-uuid-12345"
    assert payload["email"] == "test@travelmind.ai"

def test_invalid_jwt_decoding():
    invalid_token = "invalid.jwt.token.string"
    payload = decode_access_token(invalid_token)
    assert payload is None
