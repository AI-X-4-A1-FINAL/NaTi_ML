from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from models.image_generator import generate_image_with_api
from models.prompt_summarizer import summarize_prompt
import openai  # OpenAI GPT API 사용
import requests
from io import BytesIO


# image_class.py에서 ImageRequest 클래스를 임포트
from schemas.image_class import ImageRequest  # 스키마 임포트

# 라우터 인스턴스 생성
router = APIRouter()


@router.post("/generate-image")
async def generate_image(request: ImageRequest):
    """
    이미지 생성 엔드포인트
    :param request: 사용자로부터 입력받은 프롬프트와 옵션
    :return: 생성된 이미지의 URL을 JSON 형식으로 반환
    """
    try:
        
        # 프롬프트 요약 후 번역
        summarized_prompt = await summarize_prompt(request.prompt, genre=request.genre)

        # DALL·E API 호출
        image_url = generate_image_with_api(
            prompt=summarized_prompt, size=request.size
        )

        # URL에서 이미지 다운로드
        image_response = requests.get(image_url)
        
        if image_response.status_code != 200:
            raise HTTPException(status_code=500, detail="이미지 다운로드에 실패했습니다.")

        # 이미지 데이터를 byte[] 형태로 변환
        image_bytes = BytesIO(image_response.content)
        print(image_bytes)

        #return image_bytes
        
        # StreamingResponse로 이미지를 반환
        return StreamingResponse(image_bytes, media_type="image/jpeg")
    
    # 상태 코드 : 서버 오류
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"서버 오류입니다: {str(e)}")