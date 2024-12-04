# api/routes/story.py

from fastapi import APIRouter, HTTPException
from schemas.story_class import (
    StoryGenerationStartRequest,
    StoryGenerationChatRequest,
    StoryResponse
)
from service.story_service import StoryService
from models.story_generator import StoryGenerator
from models.s3_manager import S3Manager

router = APIRouter()

# S3Manager 초기화
s3_manager = S3Manager()

# StoryGenerator에 S3Manager 주입
story_generator = StoryGenerator(s3_manager=s3_manager)
story_service = StoryService(story_generator=story_generator)

@router.post("/start", response_model=StoryResponse)
async def generate_story_endpoint(request: StoryGenerationStartRequest):
    try:
        return await story_service.generate_initial_story(genre=request.genre)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/continue", response_model=StoryResponse)
async def continue_story_endpoint(request: StoryGenerationChatRequest):
    try:
        print(f"[Continue Story Endpoint] Received request: {request}")
        response = await story_service.continue_story(request)
        print(f"[Continue Story Endpoint] Generated response: {response}")
        return response
    except ValueError as e:
        print(f"[Continue Story Endpoint] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[Continue Story Endpoint] Server error: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=str(e))