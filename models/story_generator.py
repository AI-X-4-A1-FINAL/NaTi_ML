import openai
from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")

DEFAULT_AFFECTION = 50
user_game_state = {}

# ---- 스토리 생성 함수 ----
def generate_openai_response(prompt: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
    """OpenAI API를 사용해 프롬프트에 따라 응답 생성."""
    try:
        # OpenAI Chat API 사용 (새로운 API 방식)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},  # 시스템 메시지 설정
                {"role": "user", "content": prompt}  # 사용자의 프롬프트
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"].strip()  # 응답의 내용 반환
    except Exception as e:
        raise Exception(f"OpenAI API 호출 중 오류 발생: {e}")


# ---- 게임 시작 로직 ----
async def start_game(genre: str) -> Dict:
    try:
        prompt = (
            f"이 이야기는 {genre} 장르로 시작됩니다. "
            f"해당 장르에 맞는 이야기를 만들어주세요. "
        )
        
        # OpenAI API로 스토리 생성
        initial_story = generate_openai_response(prompt)

        # 초기 게임 상태 설정
        user_game_state["cut"] = 1
        user_game_state["affection"] = DEFAULT_AFFECTION

        return {
            "story": initial_story,
            "affection": DEFAULT_AFFECTION,
            "step": 1,
        }
    except Exception as e:
        raise Exception(f"게임 시작 중 오류 발생: {e}")


# ---- 스토리 생성 로직 ----
async def generate_story(user_input: str) -> Dict:
    try:
        # 게임 상태 확인
        cut = user_game_state.get("cut", 1)
        affection = user_game_state.get("affection", DEFAULT_AFFECTION)

        # 게임 종료 처리
        if cut == 11:
            ending = (
                "축하합니다! 당신은 살아남았습니다.!"
                if affection >= 80
                else "아쉽지만, 생존에 실패했습니다. 다음 생을 노려보세요."
            )
            return {"story": ending, "affection": affection, "cut": cut}

        # 스토리 생성 프롬프트 작성
        prompt = (
            f"이전 컷에서 사용자는 다음과 같은 선택을 했습니다: '{user_input}'.\n"
            f"다음 이야기를 이어서 만들어주세요. 생존율은 {affection}입니다. "
            "사용자가 선택할 수 있는 옵션을 추가하여 이야기를 이어가세요. "
            "선택지는 자연스럽게 이어지도록 하며 2~3개로 작성해주세요."
        )

        # OpenAI API로 스토리 생성
        story = generate_openai_response(prompt)

        if "친절" in story:
            affection += 10
        elif "불친절" in story:
            affection -= 5

        # 호감도 제한
        affection = max(0, min(100, affection))

        # 게임 상태 갱신
        user_game_state["cut"] = cut + 1
        user_game_state["affection"] = affection

        return {
            "story": story,
            "affection": affection,
            "cut": cut + 1,
        }

    except Exception as e:
        raise Exception(f"스토리 생성 중 오류 발생: {e}")
