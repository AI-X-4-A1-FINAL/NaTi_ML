# api/routes/story.py

from fastapi import APIRouter, HTTPException
from schemas.story_class import (
    StoryGenerationStartRequest,
    StoryGenerationChatRequest,
    StoryEndRequest,
    StoryEndResponse,
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
    """
    스토리를 생성하는 엔드포인트
    """
    try:
        response = await story_service.generate_initial_story(genre=request.genre)
        # print(f"라우트: {response}")  # 결과 로그
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")


@router.post("/continue", response_model=StoryResponse)
async def continue_story_endpoint(request: StoryGenerationChatRequest):
    """
    스토리를 이어가는 엔드포인트
    """
    try:
        # print(f"[Continue] 받은 내용: {request}")
        response = await story_service.continue_story(request)
        # print(f"[Continue] 만들어서 주는 내용 : {response}")
        return response
    except ValueError as e:
        print(f"[Continue Endpoint] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        print(f"[Continue Endpoint] Server error: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Error continuing story: {str(e)}")

@router.post("/end", response_model=StoryEndResponse)
async def generate_ending_endpoint(request: StoryEndRequest):
    """
    스토리의 마지막 엔딩을 생성하는 엔드포인트
    """
    try:
        # print(f"[End Endpoint] Received request: {request}")

        # 대화 히스토리와 유저 선택을 기반으로 엔딩 생성
        response = await story_service.generate_ending_story(
            game_id=request.game_id,
            user_choice=request.user_choice
        )

        # FastAPI 응답 생성
        final_response = {
            "story": response.get("story"),
            "survival_rate": response.get("survival_rate"),
            "game_id": request.game_id,
            "image_url": response.get("image_url")
        }
        # print(f"[End Endpoint] Generated ending: {final_response}")
        return final_response

    except ValueError as e:
        print(f"[End Endpoint] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        print(f"[End Endpoint] Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating ending: {str(e)}")
