"""تهيئة قاعدة SQLite (وضع WAL) + بيانات بذر عربية fresh."""

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine, select

from .core.config import settings
from .core.security import hash_password
from .models import ParentRequest, User

engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


def init_db() -> None:
    """إنشاء الجداول + البذر (مرة واحدة عند أول تشغيل)."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if existing is not None:
            return
        user = User(
            email=settings.seed_email,
            user_name=settings.seed_user_name,
            password_hash=hash_password(settings.seed_password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.id is not None
        session.add_all(
            [
                ParentRequest(
                    id="req_001",
                    child_name="يوسف",
                    request_type="تمديد وقت الشاشة",
                    status="pending",
                    requested_at="2026-10-09 08:30",
                    note="يحتاج 30 دقيقة إضافية لإتمام تحدي الحساب.",
                    owner_id=user.id,
                ),
                ParentRequest(
                    id="req_002",
                    child_name="سلمى",
                    request_type="فتح درس العلوم",
                    status="approved",
                    requested_at="2026-10-08 18:10",
                    note="تمت الموافقة لمراجعة درس المجموعة الشمسية.",
                    owner_id=user.id,
                ),
                ParentRequest(
                    id="req_003",
                    child_name="أمير",
                    request_type="لعبة تعليمية جديدة",
                    status="pending",
                    requested_at="2026-10-08 16:45",
                    note="بانتظار قرار الوالد قبل فتح اللعبة.",
                    owner_id=user.id,
                ),
            ]
        )
        session.commit()
