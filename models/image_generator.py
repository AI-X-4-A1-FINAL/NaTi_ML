import os
import openai
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=openai.api_key)


def generate_image_with_dalle(prompt: str, size: str = "256x256", n: int = 1) -> str:

    try:
        response = client.images.generate(
            prompt=prompt,
            size=size,
            n=n
        )
        return response.data[0].url
    
    except Exception as e:
        raise RuntimeError(f"OpenAI API 호출 중 오류 발생: {e}")
