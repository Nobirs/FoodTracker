from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)  # type: ignore


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore
