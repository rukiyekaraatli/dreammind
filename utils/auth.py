from passlib.context import CryptContext

# Şifreleme context'i oluştur
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Girilen şifre ile hash'lenmiş şifreyi doğrular.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Girilen şifreyi hash'ler.
    """
    return pwd_context.hash(password)
