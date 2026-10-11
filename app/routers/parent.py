"""مسارات الوالدين (كلها محمية بـ JWT)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from ..core.deps import get_current_user, get_session
from ..models import ParentRequest, User
from ..schemas import CreateRequestIn, PatchRequestIn, RequestOut

router = APIRouter()


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _next_request_id(session: Session) -> str:
    ids = session.exec(select(ParentRequest.id)).all()
    numbers = [
        int(i.split("_")[1]) for i in ids if i.startswith("req_") and i[4:].isdigit()
    ]
    return f"req_{(max(numbers, default=0) + 1):03d}"


@router.get("/parent/home")
def home_overview(
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """نظرة لوحة الوالدين."""
    base = _base_url(request)
    pending = session.exec(
        select(ParentRequest).where(
            ParentRequest.owner_id == user.id,
            ParentRequest.status == "pending",
        )
    ).all()
    return {
        "title": "لوحة الوالدين",
        "summary": f"مرحباً {user.user_name} — ملخص الإشراف على الأبناء.",
        "base_url": base,
        "endpoint": "/parent/home",
        "highlights": [
            {
                "label": "طلبات بانتظار القرار",
                "value": str(len(pending)),
                "detail": "تُجلب مباشرة من قاعدة البيانات.",
            },
            {
                "label": "الأبناء المرتبطون",
                "value": "3",
                "detail": "يوسف وسلمى وأمير (بيانات البذر).",
            },
        ],
        "next_actions": [
            "مراجعة الطلبات المعلقة.",
            "اعتماد الطلب التالي.",
        ],
    }


@router.get("/parent/requests")
def requests_overview(
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """قائمة طلبات الوالد (الأحدث أولاً)."""
    base = _base_url(request)
    items = session.exec(
        select(ParentRequest)
        .where(ParentRequest.owner_id == user.id)
        .order_by(ParentRequest.id.desc())  # type: ignore[attr-defined]
    ).all()
    return {
        "title": "طلبات الوالدين",
        "summary": "اعتماد الطلبات وتحديث حالاتها من مكان واحد.",
        "base_url": base,
        "endpoint": "/parent/requests",
        "post_endpoint": "/parent/requests",
        "patch_endpoint_template": "/parent/requests/{requestId}",
        "recommended_events": [
            "إنشاء طلب جديد عبر POST.",
            "تحديث الحالة عبر PATCH.",
        ],
        "requests": [RequestOut.model_validate(r).model_dump() for r in items],
    }


@router.post(
    "/parent/requests", response_model=RequestOut, status_code=status.HTTP_201_CREATED
)
def create_request(
    body: CreateRequestIn,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """إنشاء طلب جديد (400 عند نقص الحقول)."""
    child_name = body.child_name.strip()
    request_type = body.request_type.strip()
    note = body.note.strip()
    if not child_name or not request_type or not note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="child_name, request_type, and note are required.",
        )
    assert user.id is not None
    item = ParentRequest(
        id=_next_request_id(session),
        child_name=child_name,
        request_type=request_type,
        status="pending",
        requested_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        note=note,
        owner_id=user.id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return RequestOut.model_validate(item)


@router.patch("/parent/requests/{request_id}", response_model=RequestOut)
def update_request_status(
    request_id: str,
    body: PatchRequestIn,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """تحديث حالة طلب (404 للغائب، 400 لغياب الحالة)."""
    item = session.get(ParentRequest, request_id)
    if item is None or item.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No parent request exists for {request_id}.",
        )
    status_value = body.status.strip()
    if not status_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status is required for request updates.",
        )
    item.status = status_value
    if body.review_note.strip():
        item.note = body.review_note.strip()
    session.add(item)
    session.commit()
    session.refresh(item)
    return RequestOut.model_validate(item)
