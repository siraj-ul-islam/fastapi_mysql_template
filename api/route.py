from fastapi import APIRouter
from api import users, auth, notes, leads


router = APIRouter()

router.include_router(users.router)
router.include_router(auth.router)
router.include_router(notes.router)
router.include_router(leads.router)
