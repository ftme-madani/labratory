from fastapi import APIRouter
from .auth import router as auth_router
from .experiments import router as experiments_router
from .simulation import router as simulation_router
from .student import router as student_router
from .teacher import router as teacher_router
from .ai import router as ai_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router)
api_router.include_router(experiments_router)
api_router.include_router(simulation_router)
api_router.include_router(student_router)
api_router.include_router(teacher_router)
api_router.include_router(ai_router)
