from fastapi import APIRouter, HTTPException, Depends
from schemas.story_class import (
    StoryGenerationStartRequest,
    StoryGenerationChatRequest,
    StoryEndRequest,
    StoryEndResponse,
    StoryResponse,
    NPCChatRequest,
    NPCResponse,
    NPCAdviceResponse
)
from service.story_service import StoryService
from models.story_generator import StoryGenerator
from models.s3_manager import S3Manager
from functools import lru_cache


class SingletonContainer:
    def __init__(self):
        self._s3_manager = None
        self._story_generator = None
        self._story_service = None

    @property
    def s3_manager(self):
        if self._s3_manager is None:
            self._s3_manager = S3Manager()
        return self._s3_manager

    @property
    def story_generator(self):
        if self._story_generator is None:
            self._story_generator = StoryGenerator(s3_manager=self.s3_manager)
        return self._story_generator

    @property
    def story_service(self):
        if self._story_service is None:
            self._story_service = StoryService(story_generator=self.story_generator)
        return self._story_service


@lru_cache()
def get_singleton_container():
    return SingletonContainer()

# 라우터 정의
router = APIRouter()

@router.post("/start", response_model=StoryResponse)
async def generate_story_endpoint(
    request: StoryGenerationStartRequest, 
    container: SingletonContainer = Depends(get_singleton_container)
):
    try:
        response = await container.story_service.generate_initial_story(genre=request.genre)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")

@router.post("/continue", response_model=StoryResponse)
async def continue_story_endpoint(
    request: StoryGenerationChatRequest, 
    container: SingletonContainer = Depends(get_singleton_container)
):
    try:
        response = await container.story_service.continue_story(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error continuing story: {str(e)}")

@router.post("/advice", response_model=NPCAdviceResponse)
async def get_npc_advice_endpoint(
    request: NPCChatRequest, 
    container: SingletonContainer = Depends(get_singleton_container)
):
    try:
        response = await container.story_service.npc_service.get_npc_advice(request.game_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=NPCResponse)
async def chat_with_npc_endpoint(
    request: NPCChatRequest, 
    container: SingletonContainer = Depends(get_singleton_container)
):
    try:
        response = await container.story_service.chat_with_npc(request.game_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in NPC chat: {str(e)}")

@router.post("/end", response_model=StoryEndResponse)
async def generate_ending_endpoint(
    request: StoryEndRequest, 
    container: SingletonContainer = Depends(get_singleton_container)
):
    try:
        response = await container.story_service.generate_ending_story(
            game_id=request.game_id,
            user_choice=request.user_choice
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ending: {str(e)}")
