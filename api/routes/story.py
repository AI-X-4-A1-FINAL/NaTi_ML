from fastapi import APIRouter, Depends, HTTPException
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

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class S3Manager(metaclass=SingletonMeta):
    def __init__(self):
        pass

class StoryGenerator(metaclass=SingletonMeta):
    def __init__(self, s3_manager: S3Manager):
        self.s3_manager = s3_manager
        pass

class StoryService(metaclass=SingletonMeta):
    def __init__(self, story_generator: StoryGenerator):
        self.story_generator = story_generator
        pass

router = APIRouter()

def get_s3_manager():
    return S3Manager()

def get_story_generator():
    return StoryGenerator(s3_manager=get_s3_manager())

def get_story_service():
    return StoryService(story_generator=get_story_generator())

@router.post("/start", response_model=StoryResponse)
async def generate_story_endpoint(
    request: StoryGenerationStartRequest,
    story_service: StoryService = Depends(get_story_service)
):
    try:
        response = await story_service.generate_initial_story(genre=request.genre)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")

@router.post("/continue", response_model=StoryResponse)
async def continue_story_endpoint(
    request: StoryGenerationChatRequest,
    story_service: StoryService = Depends(get_story_service)
):
    try:
        response = await story_service.continue_story(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error continuing story: {str(e)}")

@router.post("/advice", response_model=NPCAdviceResponse)
async def get_npc_advice_endpoint(
    request: NPCChatRequest,
    story_service: StoryService = Depends(get_story_service)
):
    try:
        response = await story_service.npc_service.get_npc_advice(request.game_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=NPCResponse)
async def chat_with_npc_endpoint(
    request: NPCChatRequest,
    story_service: StoryService = Depends(get_story_service)
):
    try:
        response = await story_service.chat_with_npc(request.game_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in NPC chat: {str(e)}")

@router.post("/end", response_model=StoryEndResponse)
async def generate_ending_endpoint(
    request: StoryEndRequest,
    story_service: StoryService = Depends(get_story_service)
):
    try:
        response = await story_service.generate_ending_story(
            game_id=request.game_id,
            user_choice=request.user_choice
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ending: {str(e)}")