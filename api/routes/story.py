from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from models.story_generator import generate_initial_story, generate_continued_story

# 요청 모델 정의
class StartGameRequest(BaseModel):
    genre: str

class StoryRequest(BaseModel):
    genre: str
    current_stage: int
    initialStory: str
    user_input: str
    
# 라우터 객체 생성
router = APIRouter()

# 게임 시작 엔드포인트
@router.post("/start", response_model=dict)
async def start_game_endpoint(request: StartGameRequest):
    try:
        # 장르를 기반으로 초기 스토리 생성
        result = generate_initial_story(request.genre)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 스토리 게속계속 돌고도는 엔드포인트
@router.post("/chat", response_model=dict)
async def chat_endpoint(request: StoryRequest):
    try:
        # 이전 이야기와 유저 입력으로 새로운 스토리 생성
        result = generate_continued_story(
            initialStory=request.initialStory,
            user_input=request.user_input,
            genre=request.genre,
            current_stage=request.current_stage
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    