"""مسارات التطبيق العامة: نظرة الرئيسية + المصادقة."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from ..core.deps import get_session
from ..core.security import create_access_token, hash_password, verify_password
from ..models import User
from ..schemas import AuthOut, LoginIn, RegisterIn

router = APIRouter()


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@router.get("/app/home")
def home_overview(request: Request):
    """نظرة عامة للشاشة الرئيسية (عامة)."""
    base = _base_url(request)
    return {
        "headline": "نظرة عامة على تطبيق الفُلك",
        "summary": "تُغذّى هذه الشاشة من خادم FastAPI الحقيقي عبر نفس عقد Retrofit.",
        "base_url": base,
        "endpoint": "/app/home",
        "principles": [
            "عقد API واحد يخدم التطبيق",
            "مصادقة JWT حقيقية",
            "SQLite محلي بوضع WAL",
            "أشكال JSON مطابقة للتطبيق حرفياً",
        ],
        "modules": [
            {
                "name": "app_features",
                "description": "الغلاف المشترك: الرئيسية والمصادقة.",
                "status": "Ready",
                "folders": ["lib/src/features/app_features/home/"],
                "next_step": "ربط بقية الشاشات بالخادم.",
            },
            {
                "name": "parent_features",
                "description": "لوحات الوالدين والموافقات.",
                "status": "Ready",
                "folders": ["lib/src/features/parent_features/"],
                "next_step": "استكمال تدفقات الطلبات.",
            },
            {
                "name": "child_features",
                "description": "مهام الطفل وتقدمه.",
                "status": "Ready",
                "folders": ["lib/src/features/child_features/"],
                "next_step": "مزامنة المهام مع الخادم.",
            },
        ],
        "next_milestones": [
            "تغطية بقية الدومين (الأبناء، السياسات، الإشعارات).",
            "تدوير Refresh Tokens ونظام OTP.",
        ],
    }


@router.post("/app/auth/login", response_model=AuthOut)
def login(body: LoginIn, session: Session = Depends(get_session)):
    """تسجيل الدخول بالبريد وكلمة المرور (401 عند البطلان)."""
    user = session.exec(select(User).where(User.email == body.email)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return AuthOut(
        token=create_access_token(str(user.id)),
        user_name=user.user_name,
        email=user.email,
    )


@router.post("/app/auth/register", response_model=AuthOut, status_code=201)
def register(body: RegisterIn, session: Session = Depends(get_session)):
    """إنشاء حساب جديد (409 عند تكرار البريد)."""
    email = body.email.strip()
    if "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid email is required.",
        )
    if len(body.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )
    user_name = (body.user_name or "").strip() or email.split("@")[0]
    user = User(
        email=email,
        user_name=user_name,
        password_hash=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return AuthOut(
        token=create_access_token(str(user.id)),
        user_name=user.user_name,
        email=user.email,
    )
