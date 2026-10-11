"""تجزئة كلمات المرور (bcrypt) وإصدار/فك رموز JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings

# حد bcrypt الأقصى (72 بايت) — يُقطع قبله بشكل معلن بدل الخطأ.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """تجزئة كلمة المرور (لا يُخزَّن النص الصريح أبداً)."""
    raw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """التحقق من كلمة المرور مقابل التجزئة المخزنة."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8")[:_BCRYPT_MAX_BYTES],
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(subject: str) -> str:
    """إصدار JWT قصير العمر حامله معرّف المستخدم."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.secret_key,
        algorithm="HS256",
    )


def decode_subject(token: str) -> str | None:
    """استخراج معرّف المستخدم من الرمز، أو None عند البطلان/الانتهاء."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    return str(subject) if subject is not None else None
