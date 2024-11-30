from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models.image_generator import generate_image_with_dalle
from models.prompt_summarizer import summarize_prompt
from deep_translator import GoogleTranslator  
import openai 

# 라우터 인스턴스 생성
router = APIRouter()

# Request Body 스키마 정의
class ImageRequest(BaseModel):
    prompt: str  # 사용자가 입력할 프롬프트
    size: str = "1024x1024"  # 이미지 크기 (기본값 제공)
    n: int = 1  # 생성할 이미지 수 (기본값 제공)


async def summarize_prompt(prompt: str) -> str:
    """
    GPT를 사용하여 프롬프트 요약
    :param prompt: 원본 프롬프트
    :return: 요약된 프롬프트
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[ 
                {"role": "system", "content": "Summarize the following prompt briefly for image generation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Error summarizing prompt: {str(e)}")


@router.post("/generate-image")
async def generate_image(request: ImageRequest):
    """
    이미지 생성 엔드포인트
    :param request: 사용자로부터 입력받은 프롬프트와 옵션
    :return: 생성된 이미지의 URL을 JSON 형식으로 반환
    """
    try:
        # 프롬프트 요약
        summarized_prompt = await summarize_prompt(request.prompt)

        # 번역기 설정 (deep_translator 사용)
        # 한글 프롬프트를 영어로 번역
        translated_prompt = GoogleTranslator(source='ko', target='en').translate(summarized_prompt)

        # DALL·E API 호출
        response = generate_image_with_dalle(
            prompt=translated_prompt, size=request.size, n=request.n
        )

        # 응답에서 이미지 URL 추출
        image_url = response['data'][0]['url']

        # 원본 프롬프트, 요약 프롬프트, 번역 프롬프트와 함께 반환
        return JSONResponse(content={
            "originalPrompt": request.prompt,
            "summarizedPrompt": summarized_prompt,
            "translatedPrompt": translated_prompt,
            "imageUrl": image_url
        })
    
    except RuntimeError as e:
        # API 호출 중 오류 발생 시 HTTPException 반환
        raise HTTPException(status_code=500, detail=str(e))
