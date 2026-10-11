"""مسارات الطفل (محمية بـ JWT)."""

from fastapi import APIRouter, Depends, Request

from ..core.deps import get_current_user
from ..models import User

router = APIRouter()


@router.get("/child/home")
def home_overview(request: Request, user: User = Depends(get_current_user)):
    """نظرة شاشة الطفل: مهام ونصائح."""
    base = str(request.base_url).rstrip("/")
    return {
        "title": "مرحباً بك في رحلة التعلم",
        "summary": "مهامك اليومية ونقاط التقدم بانتظارك.",
        "base_url": base,
        "endpoint": "/child/home",
        "tasks": [
            {
                "title": "قراءة درس اليوم",
                "status": "completed",
                "reward": "15 نقطة",
            },
            {
                "title": "حل واجب الحساب",
                "status": "pending",
                "reward": "20 نقطة",
            },
            {
                "title": "مراجعة المفردات",
                "status": "in-progress",
                "reward": "10 نقاط",
            },
        ],
        "tips": [
            "أنجز مهامك اليومية لجمع النقاط.",
            "اطلب من والديك اعتماد المهام المنجزة.",
        ],
    }
