from fastapi import APIRouter, HTTPException, Depends
from schemas.story_class import StoryGenerationStartRequest
from service.story_service import StoryService
from models.story_generator import StoryGenerator

import os

router = APIRouter()

# StoryGenerator와 StoryService 초기화
prompt_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../prompts")
story_generator = StoryGenerator(prompt_base_path=prompt_base_path)
story_service = StoryService(story_generator=story_generator)

@router.post("/start")
async def generate_story_endpoint(request: StoryGenerationStartRequest):
    try:
        # 장르 기반 스토리 생성
        story = await story_service.generate_initial_story(genre=request.genre)
        return {"story": story}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")
