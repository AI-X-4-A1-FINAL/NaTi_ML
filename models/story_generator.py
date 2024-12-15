# models/story_generator.py

from langchain.callbacks.base import BaseCallbackHandler
import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from typing import List, Dict, Optional
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document
from models.npc_handler import NPCHandler
import re
from templates.story_templates import (
    get_romance_initial_template,
    get_survival_initial_template,
    get_romance_continue_template,
    get_survival_continue_template,
    get_romance_ending_template,
    get_survival_ending_template,
    get_survival_rate_template,
    get_romance_rate_template,
)
from functools import lru_cache

load_dotenv()

class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming responses."""
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)

class StoryGenerator:
    def __init__(self, api_key: Optional[str] = None, s3_manager=None):
        self.api_key = api_key or os.getenv("OPENAI_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.s3_manager = s3_manager
        self.model = ChatOpenAI(
            openai_api_key=self.api_key,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=500,
            streaming=True,
            callbacks=[StreamingCallbackHandler()]
        )
        self.parser = StrOutputParser()
        self.story_memory = ConversationBufferWindowMemory(k=5, return_messages=True)
        self.game_id = None

     # NPCHandler 초기화
        self.npc_handler = NPCHandler(api_key=self.api_key)

    def set_game_id(self, game_id: str):
        """game_id 설정"""
        self.game_id = game_id

    async def initialize_npc(self, story_context: str) -> str:
        """NPC 초기 인사말 생성"""
        try:
            return await self.npc_handler.generate_greeting(story_context)
        except Exception as e:
            print(f"[ERROR] Failed to initialize NPC: {e}")
            raise

    async def chat_with_npc(self, story_context: str, choices: List[str]) -> Dict:
        """NPC 조언 및 생존율 얻기"""
        try:
            npc_response = await self.npc_handler.provide_advice(story_context, choices)
            return {
                "response": npc_response["response"],
                "game_id": self.game_id or "default_id",
                "additional_comment": npc_response.get("additional_comment")
            }
        except Exception as e:
            print(f"[ERROR] Failed to chat with NPC: {e}")
            raise

    async def generate_initial_story(self, genre: str) -> Dict[str, str]:
        try:
            random_prompt = await self.s3_manager.get_random_prompt(genre)
            base_prompt = random_prompt["content"]
            file_name = random_prompt["file_name"]

            self.story_memory.save_context({"input": "System"}, {"output": base_prompt})

            # 여기를 수정 - await 추가
            if genre == "Romance":
                system_template = await get_romance_initial_template(base_prompt)
            else:
                system_template = await get_survival_initial_template(base_prompt)

            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser

            result = await chain.ainvoke({})

            if not result:
                raise ValueError("No story generated.")

            if "Story:" not in result or "Choices:" not in result:
                print("[Initial Story] ERROR: Invalid response format")
                print(f"Raw response: {result}")
                raise ValueError("Invalid story format: missing Story or Choices section")

            parts = result.split("\nChoices:")
            story = parts[0].replace("Story:", "").strip()
            choices = parts[1].strip("[] \n").split(",")
            choices = [choice.strip() for choice in choices]

            self.story_memory.save_context({"input": "Story begins"}, {"output": result})

            return {
                "story": story,
                "choices": choices,
                "file_name": file_name
            }
        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")


    async def continue_story(self, request: Dict[str, str]) -> Dict[str, str]:
        try:
            current_stage = int(request.get("stage", 1))
            user_choice = request.get("user_choice", "") 

            # 대화 메모리에서 이전 스토리 불러오기
            conversation_history = self.story_memory.load_memory_variables({}).get("history", [])
            previous_story = "\n".join(
                message.content if hasattr(message, "content") else str(message)
                for message in conversation_history
            )

            # 단계별 템플릿
            default_stage_templates = {
                1: "Introduce the setting and the initial situation. Hint at the main conflict to come.",
                2: "Develop the main conflict and build tension.",
                3: "Bring the conflict to a climax. The stakes should be higher, and choices more significant.",
                4: "Reach the turning point. Present a critical moment where the user's choice defines the resolution.",
                5: "Conclude the story. Tie up loose ends and present the final outcome based on previous choices.",
            }

            stage_template = default_stage_templates.get(current_stage, default_stage_templates[5])
            genre = request.get("genre", "Survival")

            # 템플릿 생성
            if genre == "Romance":
                template = await get_romance_continue_template(
                    stage_template=stage_template,
                    previous_story=previous_story,
                    user_choice=user_choice
                )
            else:
                template = await get_survival_continue_template(
                    stage_template=stage_template,
                    previous_story=previous_story,
                    user_choice=user_choice
                )

            prompt_template = ChatPromptTemplate.from_template(template)
            chain = prompt_template | self.model | self.parser

            # LLM 호출
            result = await chain.ainvoke({
                "previous_story": previous_story,
                "user_choice": user_choice,  
                "stage_template": stage_template
            })

            if not result:
                raise ValueError("No continuation generated.")

            # 응답 검증 및 파싱
            if "\nChoices:" not in result:
                print("[Continue Story] ERROR: 'Choices:' section missing in response.")
                print(f"Raw response: {result}")
                raise ValueError("Invalid story format: missing 'Choices:' section")

            parts = result.split("\nChoices:")
            if len(parts) < 2:
                print("[Continue Story] ERROR: Response could not be split into story and choices.")
                print(f"Raw response: {result}")
                raise ValueError("Invalid story format: could not split into story and choices.")

            story = parts[0].replace("Story:", "").strip()
            choices = parts[1].strip("[] \n").split(",")
            choices = [choice.strip() for choice in choices if choice.strip()]

            if not choices:
                raise ValueError("No valid choices extracted from response.")

            # 메모리에 현재 스토리 저장
            self.story_memory.save_context(
                {"input": user_choice},
                {"output": result}
            )

            return {
                "story": story,
                "choices": choices,
                "stage": current_stage + 1
            }
        except Exception as e:
            print(f"[Continue Story] ERROR: {str(e)}")
            raise Exception(f"Error continuing story: {str(e)}")



    async def generate_ending_story(self, conversation_history: list, genre: str = "Survival") -> dict:
        """엔딩 스토리 생성 및 생존율 계산"""
        try:
            print(f"[DEBUG] Received conversation history: {conversation_history}")

            # 대화 내용을 문자열로 변환
            conversation_text = "\n".join(
                message.content if hasattr(message, "content") else str(message)
                for message in conversation_history
            )

            # 문서 생성 및 요약
            conversation_document = [Document(page_content=conversation_text)]
            summarize_chain = load_summarize_chain(self.model, chain_type="map_reduce")
            summary_result = await summarize_chain.ainvoke({"input_documents": conversation_document})

            # 요약본 추출
            summary = (
                summary_result.get("output_text", "")
                if isinstance(summary_result, dict)
                else summary_result
            )
            if not summary:
                raise ValueError("Summary generation failed")

            print(f"[DEBUG Summary] {summary}")

            # 생존율 계산 템플릿 선택 및 호출
            if genre == "Romance":
                rate_template = await get_romance_rate_template(summary=summary)
            else:
                rate_template = await get_survival_rate_template(summary=summary)

            rate_prompt = ChatPromptTemplate.from_template(rate_template)
            rate_chain = rate_prompt | self.model | self.parser

            # 생존율 계산
            rate_result = await rate_chain.ainvoke({"summary": summary})

            survival_rate = 0
            try:
                # 숫자만 추출
                import re
                numbers = re.findall(r'\d+', str(rate_result))
                if numbers:
                    survival_rate = min(100, max(0, int(numbers[0])))
                else:
                    survival_rate = 50  # 기본값
            except ValueError:
                survival_rate = 50  # 기본값

            print(f"[DEBUG Survival Rate] {survival_rate}%")

            # 엔딩 스토리 생성 템플릿 선택 및 호출
            if genre == "Romance":
                ending_template = await get_romance_ending_template(
                    conversation_text=conversation_text,
                    summary=summary
                )
            else:
                ending_template = await get_survival_ending_template(
                    conversation_text=conversation_text,
                    summary=summary
                )

            ending_prompt = ChatPromptTemplate.from_template(ending_template)
            ending_chain = ending_prompt | self.model | self.parser

            # 엔딩 스토리 생성
            ending_story_result = await ending_chain.ainvoke({
                "conversation_text": conversation_text,
                "summary": summary
            })

            ending_story = (
                ending_story_result.get("text", "")
                if isinstance(ending_story_result, dict)
                else str(ending_story_result).strip()
            )
            if not ending_story:
                raise ValueError("No ending generated")

            print(f"[DEBUG Ending Story] {ending_story}")

            return {
                "summary": summary.strip(),
                "survival_rate": survival_rate,
                "ending_story": ending_story,
                "npc_final_message": "이야기가 끝났네요. 당신의 선택에 따라 모든 것이 달라졌습니다."
            }

        except Exception as e:
            print(f"[Ending Story ERROR] {str(e)}")
            return {
                "summary": "스토리 요약을 생성하지 못했습니다.",
                "survival_rate": 50,  # 기본값
                "ending_story": "예기치 못한 상황으로 인해 엔딩을 생성하지 못했습니다.",
                "npc_final_message": "이야기가 끝났네요. 당신의 선택에 따라 모든 것이 달라졌습니다."
            }



@lru_cache()
def get_story_generator(api_key: Optional[str] = None, s3_manager=None) -> StoryGenerator:
    return StoryGenerator(api_key=api_key, s3_manager=s3_manager)