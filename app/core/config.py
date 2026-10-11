"""إعدادات التطبيق من متغيرات البيئة (مع قيم تطوير آمنة افتراضياً)."""

import os
import warnings


class Settings:
    """تُقرأ مرة واحدة عند الاستيراد."""

    secret_key: str = os.environ.get(
        "SECRET_KEY", "dev-only-insecure-secret-key-change-me"
    )
    access_token_expire_minutes: int = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./elfulk.db")
    seed_email: str = os.environ.get("SEED_EMAIL", "parent@elfulk.app")
    seed_password: str = os.environ.get("SEED_PASSWORD", "Seed123!")
    seed_user_name: str = os.environ.get("SEED_USER_NAME", "ولي الأمر")


settings = Settings()

if settings.secret_key == "dev-only-insecure-secret-key-change-me":
    warnings.warn(
        "SECRET_KEY يستخدم القيمة التطويرية الافتراضية — اضبطه من البيئة في الإنتاج!",
        UserWarning,
        stacklevel=2,
    )
