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
            f"지금 '{genre}' 이 장르에 맞는 내용의 게임 세계관을 만들어줘야해. "
            "한글로 말하고, 한번 말할 때 마다 200자 이내로 말하면 돼"
            "유저에게 상황과 함께 어떤 선택을 할지 2~3개의 선택지를 주도록해"
            "선택에 따라서 생존확률을 계산할꺼야. 생존확률은 너만 알고있고 계속 기억하고 있어야해"
            "계속 이어서 스토리를 만들어줘"
            "스토리가 갑자기 다른 이야기로 가거나 하면 안돼" 
        )

        # OpenAI Chat API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 게임 스토리텔링의 전문가야. 한글로 대답해"},
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
    
# 돌고도는 이야기
def generate_continued_story(initialStory: str, userInput: str, genre: str, currentStage: int) -> Dict:
    try:
        prompt = (
            f"장르: '{genre}'\n"
            f"현재 단계: {currentStage}\n"
            f"이전 이야기: '{initialStory}'\n\n"
            f"유저의 입력: '{userInput}'\n\n"
            "유저 입력을 바탕으로 이야기를 이어가. 한 번 말할 때 200자 이내로 말하고, 상황에 맞는 2~3개의 선택지를 줘. "
            "스토리가 갑자기 다른 이야기로 변하면 안 돼."
            "장르, 현재 단계, 이전 이야기를 유저에게 해주지 마."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 게임 스토리텔링의 전문가야. 한글로 대답해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return {"story": response["choices"][0]["message"]["content"].strip()}
    except Exception as e:
        raise Exception(f"Error generating continued story: {e}")