from fastapi import APIRouter
from api import users, auth, notes


router = APIRouter()

router.include_router(users.router)
router.include_router(auth.router)
router.include_router(notes.router)
