from langchain.callbacks.base import BaseCallbackHandler
import os
import uuid
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from typing import Optional, Dict
import random


load_dotenv()

class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming responses."""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is received."""
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
        self.memory = ConversationBufferWindowMemory(k=5, return_messages=True)
        self.game_id = None

    def set_game_id(self, game_id: str):
        """game_id 설정"""
        self.game_id = game_id    
        
    async def generate_initial_story(self, genre: str) -> Dict[str, str]:
        try:
            base_prompt = await self.s3_manager.get_random_prompt(genre)
            print(f"[Initial Story] Retrieved base prompt from S3")

            self.memory.save_context({"input": "System"}, {"output": base_prompt})

            system_template = (
                "You are a master storyteller specializing in narrative creation. "
                f"{base_prompt}\n"
                "The story should be written in Korean, maintaining proper narrative flow "
                "and cultural context. Keep the response under 500 characters. "
                "End with exactly 3 survival choices. Format: 'Story: [text]\nChoices: [1,2,3]'"
            )

            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser

            result = await chain.ainvoke({})
            print(f"[Initial Story] Generated result: {result}")

            if not result:
                raise ValueError("No story generated.")

            # 응답 형식 검증
            if "Story:" not in result or "Choices:" not in result:
                print("[Initial Story] ERROR: Invalid response format")
                print(f"Raw response: {result}")
                raise ValueError("Invalid story format: missing Story or Choices section")

            # Story와 Choices 분리
            parts = result.split("\nChoices:")
            story = parts[0].replace("Story:", "").strip()
            choices = parts[1].strip("[] \n").split(",")
            choices = [choice.strip() for choice in choices]

            self.memory.save_context({"input": "Story begins"}, {"output": result})

            return {
                "story": story,
                "choices": choices
            }

        except Exception as e:
            print(f"[Initial Story] ERROR: {str(e)}")
            raise Exception(f"Error generating story: {str(e)}")

    async def continue_story(self, request: Dict[str, str]) -> Dict[str, str]:
        try:
            print(f"[Continue Story] Received request: {request}")

            # 유저의 초이스 횟수 추적 (스테이지 번호)
            if "stage" in request:
                current_stage = int(request["stage"])  # 현재 초이스 횟수
            else:
                current_stage = 1  # 기본값은 1단계

            print(f"[Continue Story] Current stage (choice count): {current_stage}")

            # 대화 히스토리 로드
            conversation_history = self.memory.load_memory_variables({}).get("history", [])
            print(f"[Continue Story] Current conversation history: {conversation_history}")

            # 기승전결에 따른 스토리 전개 템플릿
            stage_prompts = {
                1: "Introduce the setting and the initial situation. Hint at the main conflict to come.",
                2: "Develop the main conflict and build tension. Introduce challenges or obstacles.",
                3: "Bring the conflict to a climax. The stakes should be higher, and choices more significant.",
                4: "Reach the turning point. Present a critical moment where the user's choice defines the resolution.",
                5: "Conclude the story. Tie up loose ends and present the final outcome based on previous choices.",
            }

            # 스테이지에 따른 프롬프트 설정
            stage_prompt = stage_prompts.get(current_stage, stage_prompts[5])  # 기본값은 결말

            # 시스템 템플릿 생성
            system_template = (
                f"You are a master storyteller continuing an ongoing narrative. "
                f"{stage_prompt}\n"
                "Previous context: {conversation_history}\n"
                "User input: {user_input}\n"
                "Continue the story in Korean, keeping the response under 300 characters. "
                "Add fun elements and twists."
                "End with exactly 3 new choices. Format: 'Story: [text]\nChoices: [1,2,3]'"
            )

            # 프롬프트 템플릿 및 체인 구성
            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser

            # 체인 실행
            result = await chain.ainvoke({
                "conversation_history": conversation_history,
                "user_input": request.get("user_choice", "")
            })

            print(f"[Continue Story] Received result from LLM: {result}")

            if not result:
                raise ValueError("No continuation generated.")

            # 응답 형식 검증 및 파싱
            if "Story:" not in result or "Choices:" not in result:
                print("[Continue Story] ERROR: Invalid response format")
                print(f"Raw response: {result}")
                raise ValueError("Invalid story format: missing Story or Choices section")

            # Story와 Choices 분리
            parts = result.split("\nChoices:")
            story = parts[0].replace("Story:", "").strip()
            choices = parts[1].strip("[] \n").split(",")
            choices = [choice.strip() for choice in choices]

            # 메모리에 저장
            self.memory.save_context({"input": request.get("user_choice", "")}, {"output": result})

            return {
                "story": story,
                "choices": choices,
                "stage": current_stage + 1  # 다음 스테이지로 진행
            }

        except Exception as e:
            print(f"[Continue Story] ERROR: {str(e)}")
            print(f"[Continue Story] Error type: {type(e)}")
            raise Exception(f"Error continuing story: {str(e)}")

        
async def generate_ending_story(self, conversation_history: list) -> dict:
        """
        엔딩 스토리를 생성하는 로직
        """
        try:
            print(f"[Ending Story] Using conversation history: {conversation_history}")
            
            # 엔딩 프롬프트 템플릿 정의
            system_template = (
                "You are a master storyteller concluding an epic narrative. "
                "Based on the conversation history provided, create a compelling ending to the story.\n"
                "Conversation history: {conversation_history}\n"
                "Conclude the story in Korean, keeping the response under 500 characters. "
                "No choices are needed, just a final closure to the narrative."
            )
            
            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser
            
            # 체인 실행
            result = await chain.ainvoke({
                "conversation_history": conversation_history
            })
            
            print(f"[Ending Story] Generated ending: {result}")
            
            if not result:
                raise ValueError("No ending generated.")
            
            return {"story": result.strip()}
        
        except Exception as e:
            print(f"[Ending Story] ERROR: {str(e)}")
            raise Exception(f"Error generating ending story: {str(e)}")