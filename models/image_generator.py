import openai
import os
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=openai.api_key)

def generate_image_with_dalle(prompt: str, size: str = "1024x1024", n: int = 1) -> dict:
    """
    DALL·E API를 사용하여 이미지를 생성하는 함수
    :param prompt: 이미지 생성에 사용할 프롬프트
    :param size: 이미지 크기 (기본값: "1024x1024")
    :param n: 생성할 이미지 수 (기본값: 1)
    :return: API 응답 데이터 (dict)
    """
    
    try:
        # prompt = "the image depicts a dark and suspenseful atmosphere with zombies." + prompt
        response = client.images.generate(
            prompt=prompt,
            size=size,
            n=n,
        )
        # print(type(response))
        # print(response)
        # print(response.data)
        image_url = response.data[0].url
        return image_url
    
    except Exception as e:
        raise RuntimeError(f"OpenAI API 호출 중 오류 발생: {e}")