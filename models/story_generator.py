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
        self.story_id = None
        self.fixed_prompt = None

    async def generate_initial_story(self, genre: str) -> Dict[str, str]:
        try:
            self.story_id = str(uuid.uuid4())
            print(f"[Initial Story] Generated new story_id: {self.story_id}")
            
            # S3에서 랜덤 프롬프트 가져오기
            if not self.fixed_prompt:  # 고정된 프롬프트가 없을 때만 랜덤으로 가져옴
                self.fixed_prompt = await self.s3_manager.get_random_prompt(genre)
                print(f"[Initial Story] Retrieved and fixed base prompt from S3")

            base_prompt = self.fixed_prompt
            print(f"[Initial Story] Using fixed prompt: {base_prompt[:50]}...") 
            
            self.memory.save_context({"input": "System"}, {"output": base_prompt})

            system_template = (
                "You are a master storyteller specializing in narrative creation. "
                f"{base_prompt}\n"
                "The story should be written in Korean, maintaining proper narrative flow "
                "and cultural context. Keep the response under 500 characters. "
                "End with exactly 3 survival choices. Give the option to choose a character. Format: 'Story: [text]\nChoices: [1,2,3]'"
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
                "choices": choices,
                "story_id": self.story_id
            }

        except Exception as e:
            print(f"[Initial Story] ERROR: {str(e)}")
            raise Exception(f"Error generating story: {str(e)}")

    async def continue_story(self, request: Dict[str, str]) -> Dict[str, str]:
        try:
            print(f"[Continue Story] Received request: {request}")

            # story_id 설정
            if "story_id" in request:
                self.story_id = request["story_id"]
                print(f"[Continue Story] Using story_id from request: {self.story_id}")
            elif not self.story_id:
                self.story_id = str(uuid.uuid4())
                print(f"[Continue Story] Generated new story_id: {self.story_id}")

            # 고정된 초기 프롬프트 사용
            base_prompt = self.fixed_prompt
            if not base_prompt:
                raise Exception("Fixed prompt not found. Initial story must be generated first.")

            conversation_history = self.memory.load_memory_variables({}).get("history", [])
            print(f"[Continue Story] Current conversation history: {conversation_history}")

            system_template = (
                "You are a master storyteller continuing an ongoing narrative. "
                "Based on the previous context and user's choice, continue the story.\n"
                "Previous context: {conversation_history}\n"
                "User input: {base_prompt}\n"
                "Continue the story in Korean, keeping response under 500 characters. "
                "End with exactly 3 new choices. Format: 'Story: [text]\nChoices: [1,2,3]'"
            )

            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser

            # 스트리밍 결과 생성
            streaming_handler = StreamingCallbackHandler()
            result = await chain.ainvoke({
                "conversation_history": conversation_history,
                "base_prompt": base_prompt,
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

            self.memory.save_context({"input": request.get("user_choice", "")}, {"output": result})

            # 스트리밍 응답을 생성하기 위한 메서드
            async def stream_story():
                """비동기적으로 토큰을 스트리밍하며 이야기를 전달."""
                for token in streaming_handler.get_token_buffer():
                    yield {"story": token}  # 실시간으로 토큰을 반환

            # 최종 반환
            return {
                "story": story,
                "choices": choices,
                "story_id": self.story_id,
                "streaming": stream_story()  # 클라이언트는 stream_story()로 데이터를 스트리밍받을 수 있음
            }

        except Exception as e:
            print(f"[Continue Story] ERROR: {str(e)}")
            print(f"[Continue Story] Error type: {type(e)}")
            print(f"[Continue Story] Full error details: {e.__dict__}")
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
