import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")

def generate_image_with_dalle(prompt: str, size: str = "1024x1024", n: int = 1) -> dict:
    """
    DALL·E API를 사용하여 이미지를 생성하는 함수
    :param prompt: 이미지 생성에 사용할 프롬프트
    :param size: 이미지 크기 (기본값: "1024x1024")
    :param n: 생성할 이미지 수 (기본값: 1)
    :return: API 응답 데이터 (dict)
    """
    try:
        response = openai.Image.create(
            prompt=prompt,
            size=size,
            n=n,
        )
        return response
    except Exception as e:
        raise RuntimeError(f"OpenAI API 호출 중 오류 발생: {e}")
