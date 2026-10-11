"""أشكال الدخل/الخرج (Pydantic) — المفاتيح مطابقة لعقد Flutter حرفياً."""

from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    email: str
    password: str


class RegisterIn(BaseModel):
    user_name: str | None = None
    email: str
    password: str


class AuthOut(BaseModel):
    """رد المصادقة — المفتاح userName بصيغة camelCase كما يتوقع التطبيق."""

    model_config = ConfigDict(populate_by_name=True)

    token: str
    user_name: str = Field(alias="userName")
    email: str


class CreateRequestIn(BaseModel):
    child_name: str
    request_type: str
    note: str


class PatchRequestIn(BaseModel):
    status: str
    review_note: str = ""


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    child_name: str
    request_type: str
    status: str
    requested_at: str
    note: str
