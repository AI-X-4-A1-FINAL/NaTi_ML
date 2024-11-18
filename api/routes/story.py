from fastapi import APIRouter, HTTPException
from models.story_generator import start_game, generate_story
from pydantic import BaseModel
from typing import Optional

# 요청 모델 정의
class StartGameRequest(BaseModel):
    genre: str  # 장르를 받아오는 모델

class StoryRequest(BaseModel):
    user_input: str = ""

# 라우터 객체 생성
router = APIRouter()

# 게임 시작 엔드포인트
@router.post("/start-love", response_model=dict)
async def start_game_endpoint(request: StartGameRequest):
    try:
        # 모델에서 게임 시작
        result = await start_game(request.genre)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 스토리 생성 엔드포인트
@router.post("/generate-love", response_model=dict)
async def generate_story_endpoint(request: StoryRequest):
    try:
        # 모델에서 스토리 생성
        result = await generate_story(request.user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
