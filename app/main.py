"""نقطة دخول خادم الفُلك (FastAPI)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import init_db
from .routers import app as app_router
from .routers import child as child_router
from .routers import parent as parent_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield


app = FastAPI(title="elFulk Server", version="0.1.0", lifespan=lifespan)

app.include_router(app_router.router)
app.include_router(parent_router.router)
app.include_router(child_router.router)


@app.get("/")
def read_root():
    """فحص الحياة والاتصال."""
    return {"Hello": "World"}
