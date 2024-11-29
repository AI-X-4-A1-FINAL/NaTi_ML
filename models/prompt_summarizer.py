import openai
import os
from dotenv import load_dotenv


# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")


async def summarize_prompt(prompt: str, genre: str = None, theme: str = None) -> str:
    """
    GPT를 사용하여 프롬프트 요약
    :param prompt: 원본 프롬프트
    :param genre: 장르 (예: 판타지, SF, 공포 등)
    :param theme: 테마 (예: 좀비, 마법, 우주 등)
    :return: 요약된 프롬프트
    """
    try:
        # 기본 요약 지시 메시지
        system_message = "Summarize the following prompt briefly for image generation."

        # 장르와 테마 정보가 있을 경우 이를 추가하여 모델에게 전달
        if genre:
            system_message += f" The genre is {genre}."
        if theme:
            system_message += f" The theme is {theme}."

        # OpenAI API 요청

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Error summarizing prompt: {str(e)}")
