from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from .config import settings
from .database import engine, Base
from .api.v1 import api_router
from .models import User, Experiment, ExperimentAttempt, StepActionLog, HintUsage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # اطمینان از ایجاد جداول پایگاه داده در زمان بالا آمدن برنامه
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="سرویس وب و موتور شبیه‌سازی هوشمند آزمایشگاه مجازی علوم تجربی دوره متوسطه (پروژه پایان‌نامه کارشناسی مهندسی کامپیوتر)",
    version="1.0.0",
    lifespan=lifespan
)

# پیکربندی CORS برای اتصال کلاینت فرانت‌اند Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# اتصال روترهای اصلی API
app.include_router(api_router, prefix="/api")

@app.get("/api/health", tags=["Health & Diagnostics"])
def health_check():
    """
    بررسی وضعیت زنده بودن سرویس و پاسخ‌دهی به کلاینت‌ها
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/detect")
async def dummy_detect_ws(websocket: WebSocket):
    try:
        await websocket.accept()
        await websocket.close()
    except (WebSocketDisconnect, Exception):
        pass
