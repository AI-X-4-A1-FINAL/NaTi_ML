from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.story_generator import generate_story

# FastAPI 라우터 설정
router = APIRouter()

# 요청 모델 정의
class StoryRequest(BaseModel):
    genre: str
    prompt: str

# 스토리 생성 API 엔드포인트
@router.post("/start")
async def generate_story_endpoint(request: StoryRequest):
    try:
        # LangChain을 사용해 스토리 생성
        response = generate_story(request.genre, request.prompt)
        return {"story": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")
