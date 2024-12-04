# api/routes/story.py

from fastapi import APIRouter, HTTPException
from schemas.story_class import (
    StoryGenerationStartRequest,
    StoryGenerationChatRequest,
    StoryResponse
)
from service.story_service import StoryService
from models.story_generator import StoryGenerator

router = APIRouter()
story_service = StoryService(story_generator=StoryGenerator())

@router.post("/start", response_model=StoryResponse)
async def generate_story_endpoint(request: StoryGenerationStartRequest):
    try:
        return await story_service.generate_initial_story(genre=request.genre)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/continue", response_model=StoryResponse)
async def continue_story_endpoint(request: StoryGenerationChatRequest):
    try:
        return await story_service.continue_story(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))