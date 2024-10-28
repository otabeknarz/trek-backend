from fastapi import APIRouter
from .views import router as core_router

router = APIRouter()

router.include_router(core_router, prefix="", tags=["core"])
