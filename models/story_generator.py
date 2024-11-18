import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---- 설정 ----
PROMPT_FILE_PATH = "storyprompts/love.txt"
DEFAULT_AFFECTION = 50

# 게임 상태를 서버 내에서 관리하기 위한 변수 (세션 상태처럼)
user_game_state = {}

# 게임 시작 로직
async def start_game(genre: str) -> Dict:
    try:
        # 초기 게임 데이터 생성 로직
        initial_story = "이 이야기는 사랑 장르로 시작됩니다. 당신은 도심 속 작은 카페에서 일하는 바리스타입니다. 오늘은 우연히 매일 오던 단골손님, 민재와 눈이 마주칩니다. 민재는 항상 밝은 표정을 지니고 있어 마음이 끌립니다."
        affection = DEFAULT_AFFECTION  # 기본 호감도
        step = 1  # 게임의 첫 번째 단계

        # 사용자의 게임 상태를 초기화 (cut 값 포함)
        user_game_state["cut"] = step
        user_game_state["affection"] = affection

        return {"story": initial_story, "affection": affection, "step": step}
    except Exception as e:
        raise Exception(f"Error starting game: {e}")

# 스토리 생성 로직
async def generate_story(user_input: str) -> Dict:
    try:
        # 게임 상태에서 cut 값을 가져옵니다.
        cut = user_game_state.get("cut", 1)
        affection = user_game_state.get("affection", DEFAULT_AFFECTION)

        # 게임 종료 처리 (cut이 10일 경우 종료)
        if cut == 11:
            if affection >= 80:
                ending = "축하합니다! 당신은 연인이 되었습니다!"
            else:
                ending = "아쉽지만, 연애에 실패했습니다. 다음 기회를 노려보세요."
            return {"story": ending, "affection": affection, "cut": cut}

        # 프롬프트 파일 읽기
        try:
            with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
                prompt_template = file.read()
        except FileNotFoundError:
            raise Exception("Prompt file not found.")
        except Exception as e:
            raise Exception(f"Error reading prompt file: {e}")

        # 스토리 생성 로직
        initial_prompt = f"이전 컷에서 사용자는 다음과 같은 선택을 했습니다: '{user_input}'.\n다음 이야기를 이어서 만들어주세요. 호감도는 {affection}입니다."

        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 연애 시뮬레이션 게임의 스토리 작가입니다."},
                {"role": "user", "content": initial_prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        story = response['choices'][0]['message']['content'].strip()

        # 호감도 업데이트
        if "친절" in story:
            affection += 10
        elif "불친절" in story:
            affection -= 5

        affection = max(0, min(100, affection))  # 호감도 0~100 범위 제한

        # cut 값 증가 (다음 컷으로 넘어가도록)
        user_game_state["cut"] = cut + 1
        user_game_state["affection"] = affection

        return {"story": story, "affection": affection, "cut": cut + 1}

    except Exception as e:
        raise Exception(f"Error generating story: {e}")
