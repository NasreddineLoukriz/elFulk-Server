# خادم الفُلك (elFulk Server)

خلفية **FastAPI** + **SQLite** + **JWT** لتطبيق الفُلك (المنزل الآمن).
تطابق مسارات وأشكال JSON التي يتوقعها التطبيق حرفياً لتحل محل
`DummyApiInterceptor` دون أي تغيير في كود Flutter.

> مسار موازٍ لخلفية الفريق (NestJS + PostgreSQL): نفس الدومين
> (Parent → Children، طلبات، مهام)، بعقد مسارات التطبيق.

## التشغيل

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ثم اضبط SECRET_KEY
uvicorn app.main:app --reload --port 8000
```

## المسارات (كلها مطابقة لعقد التطبيق)

| المسار | الطريقة | الحماية | الوصف |
|---|---|---|---|
| `/` | GET | — | فحص الحياة |
| `/app/home` | GET | — | نظرة الرئيسية |
| `/app/auth/login` | POST | — | `{email,password}` ← `{token,userName,email}` |
| `/app/auth/register` | POST | — | إنشاء حساب (409 للتكرار) |
| `/parent/home` | GET | JWT | لوحة الوالدين |
| `/parent/requests` | GET | JWT | قائمة الطلبات (الأحدث أولاً) |
| `/parent/requests` | POST | JWT | إنشاء طلب (201، و400 لنقص الحقول) |
| `/parent/requests/{id}` | PATCH | JWT | تحديث الحالة (404 للغائب) |
| `/child/home` | GET | JWT | مهام الطفل ونصائحه |

الأخطاء بشكل `{"detail": ...}` كما يفهمها التطبيق.
صيغة التاريخ: `"YYYY-MM-DD HH:MM"` كما يتوقع نموذج الطلب.

## الاختبارات

```bash
python -m pytest tests/ -q
```

## ربط التطبيق

وجّه `apiBaseUrl` في التطبيق إلى `http://<host>:8000`
(للمحاكي: `http://10.0.2.2:8000`).

## خارج النطاق حالياً (المرحلة 2)

CRUD الآباء/الأبناء، سياسات الوصول، PIN، أدوار المشرفين،
تدوير Refresh Tokens، OTP، OAuth — تقارباً مع خلفية الفريق.
