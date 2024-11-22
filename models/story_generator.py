import openai
from dotenv import load_dotenv
import os
from typing import Dict

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")

# 초기 스토리 생성 함수
def generate_initial_story(genre: str) -> Dict:
    """OpenAI를 사용해 초기 스토리를 생성"""
    try:
        # 프롬프트 정의
        prompt = (
            f"Create an engaging opening story in the '{genre}' genre. "
            "Make sure it hooks the audience and sets the tone for the game."
        )

        # OpenAI Chat API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative writer specializing in storytelling."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        # 응답 반환
        return {
            "story": response["choices"][0]["message"]["content"].strip()
        }
    except Exception as e:
        raise Exception(f"Error generating initial story: {e}")
