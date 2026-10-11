"""تعريف الجداول (SQLModel) — مطابقة لعقد تطبيق Flutter."""

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """حساب مستخدم (وليّ أمر في المرحلة 1)."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    user_name: str
    password_hash: str


class ParentRequest(SQLModel, table=True):
    """طلب من سير عمل موافقات الوالدين (المعرّف نصي كما يتوقع التطبيق)."""

    id: str = Field(primary_key=True)  # مثال: req_001
    child_name: str
    request_type: str
    status: str = "pending"
    requested_at: str  # صيغة "YYYY-MM-DD HH:MM" كما يتوقع التطبيق
    note: str = ""
    owner_id: int | None = Field(default=None, foreign_key="user.id", index=True)
