import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")

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
