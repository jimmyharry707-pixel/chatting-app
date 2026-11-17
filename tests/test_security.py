"""Password hash regression tests."""
from server.security import hash_password,verify_password

def test_password_hash_is_not_plaintext():
    digest=hash_password("correct-horse-battery")
    assert digest!="correct-horse-battery"
    assert "pbkdf2_sha256$" in digest

def test_password_hash_verifies_correct_secret():
    digest=hash_password("correct-horse-battery")
    assert verify_password("correct-horse-battery",digest)

def test_password_hash_rejects_wrong_secret():
    digest=hash_password("correct-horse-battery")
    assert not verify_password("incorrect-secret",digest)

def test_password_hash_uses_unique_salts():
    first=hash_password("same-secret")
    second=hash_password("same-secret")
    assert first!=second
