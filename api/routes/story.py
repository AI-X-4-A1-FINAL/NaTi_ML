from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_story():
    return {"message": "Story API"}
