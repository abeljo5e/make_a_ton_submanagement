import pytest
from fastapi import HTTPException
from app.core.security import (
    validate_password_strength,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_reset_token,
    hash_reset_token,
)


def test_password_validation_strong():
    is_valid, err = validate_password_strength("BrightLoop#2026")
    assert is_valid is True
    assert err is None


def test_password_validation_too_short():
    is_valid, err = validate_password_strength("Ab1!")
    assert is_valid is False
    assert "longer than 8 characters" in err


def test_password_validation_no_uppercase():
    is_valid, err = validate_password_strength("brightloop#2026")
    assert is_valid is False
    assert "uppercase" in err


def test_password_validation_no_lowercase():
    is_valid, err = validate_password_strength("BRIGHTLOOP#2026")
    assert is_valid is False
    assert "lowercase" in err


def test_password_validation_no_digit():
    is_valid, err = validate_password_strength("BrightLoop#Secure")
    assert is_valid is False
    assert "numeric digit" in err


def test_password_validation_no_special():
    is_valid, err = validate_password_strength("BrightLoop2026")
    assert is_valid is False
    assert "special character" in err


def test_bcrypt_hashing_and_verification():
    raw = "MySuperSecret$2026"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongSecret$2026", hashed) is False


def test_jwt_create_and_decode():
    payload = {"sub": "e6a2b890-3490-4c6e-82f7-bf84ef9b3a4e", "role": "admin"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["sub"] == payload["sub"]
    assert decoded["role"] == payload["role"]
    assert "exp" in decoded
    assert "iat" in decoded


def test_jwt_invalid_token():
    with pytest.raises(HTTPException) as exc:
        decode_access_token("not-a-valid-token")
    assert exc.value.status_code == 401


def test_reset_token_generation_and_hashing():
    raw_token, token_hash = generate_reset_token()
    assert len(raw_token) >= 32
    assert hash_reset_token(raw_token) == token_hash
