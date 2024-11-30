from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.story_class import StoryGenerationRequest
from core.s3_manager import S3Manager
from service.story_service import StoryService
from models.story_generator import StoryGenerator

router = APIRouter()

s3_manager = S3Manager()
story_generator = StoryGenerator()
story_service = StoryService(s3_manager, story_generator)

# 요청 데이터를 의존성으로 처리
def get_story_generation_request(request: StoryGenerationRequest):
    return request

@router.post("/start")
async def generate_story_endpoint(
    request: StoryGenerationRequest = Depends(get_story_generation_request)
):
    try:
        # 하나의 객체로 모든 데이터를 전달
        story = await story_service.generate_initial_story(
            genre=request.genre, 
            tags=request.tags
        )
        return {"story": story}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")

@router.post("/chat")
async def continue_story(
    request: StoryGenerationRequest = Depends(get_story_generation_request)
):
    try:
        conversation_history = request.conversationHistory or []
        story = await story_service.continue_story(
            genre=request.genre, 
            initialStory=request.initialStory, 
            userInput=request.userInput, 
            conversation_history=conversation_history
        )
        return {"story": story, "conversationHistory": conversation_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")
