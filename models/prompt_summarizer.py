# models/prompt_summarizer.py

import openai
import os
from dotenv import load_dotenv


# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_KEY")


async def summarize_prompt(prompt: str, genre: str = None) -> str:
    """
    GPT를 사용하여 프롬프트 요약
    :param prompt: 원본 프롬프트
    :param genre: 장르 (예: 재난, 좀비, 외계인 등)
    :return: 요약된 프롬프트
    """
    try:
        # 먼저 원본 프롬프트를 요약
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "Summarize and translate the following prompt into English. "
                    "Focus on key visual elements, settings, objects, and colors."
                    "Avoid unnecessary descriptive language."
                )},
                {"role": "user", "content": prompt}  # 원본 프롬프트를 요약
            ],            
            max_tokens=50,
            temperature=0.5
        )

        # 요약된 프롬프트
        summarized_prompt = response.choices[0].message.content

        # 뒤에 고정으로 나오는 프롬프트
        style = ", cinematic photograph, explosive action, high contrast, dynamic lightning."
        
        # genre에 따라 사전 정의된 프롬프트 설정
        if genre == "Survival":
            newPrompt = "very depressed atmosphere " + summarized_prompt + style
        elif genre == "좀비":
            newPrompt = "Post-apocalyptic scene with abandoned streets and hordes of zombies." + summarized_prompt + style
        elif genre == "외계인":
            newPrompt = "Surreal dreamscape with floating islands and impossible architecture. " + summarized_prompt + style
        else:
            # 장르가 정의되지 않으면 원본 프롬프트 그대로 사용
            newPrompt = summarized_prompt + " " + style

        # 최종적으로 새로운 프롬프트 반환
        return newPrompt
    
    except Exception as e:
        raise RuntimeError(f"Error summarizing prompt: {str(e)}")
