"""اعتماديات FastAPI: الجلسة + المستخدم الحالي من JWT."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from ..db import engine
from ..models import User
from .security import decode_subject

_bearer = HTTPBearer(auto_error=False)


def get_session():
    with Session(engine) as session:
        yield session


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    """يستخرج المستخدم من `Authorization: Bearer <JWT>` (401 عند غيابه/بطلانه)."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    subject = decode_subject(credentials.credentials)
    user = (
        session.get(User, int(subject))
        if subject is not None and subject.isdigit()
        else None
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    return user
