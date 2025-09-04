from fastapi import APIRouter
from api.exit_record import router as exit_record_router
from api.permissions import router as permissions_router

api_router = APIRouter()

api_router.include_router(exit_record_router, prefix="/exit_record", tags=["exit_record"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["permissions"])


