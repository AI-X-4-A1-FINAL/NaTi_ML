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
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document


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

            raise Exception(f"Error generating story: {str(e)}")

    async def continue_story(self, request: Dict[str, str]) -> Dict[str, str]:
        try:

            # 유저의 초이스 횟수 추적 (스테이지 번호)
            if "stage" in request:
                current_stage = int(request["stage"])  # 현재 초이스 횟수
            else:
                current_stage = 1  # 기본값은 1단계


            # 대화 히스토리 로드
            conversation_history = self.memory.load_memory_variables({}).get("history", [])

            # 기승전결에 따른 스토리 전개 템플릿
            stage_prompts = {
                1: "Introduce the setting and the initial situation. Hint at the main conflict to come.",
                2: "Develop the main conflict and build tension. ",
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
        엔딩 스토리를 생성하고 생존율을 계산하는 로직
        """
        try:
            print(f"[DEBUG] Received conversation history: {conversation_history}")

            # Step 1: HumanMessage 객체를 문자열로 변환
            conversation_text = "\n".join(
                message.content if hasattr(message, "content") else str(message)
                for message in conversation_history
            )

            # Step 2: 문자열을 Document 객체로 변환 (summarize_chain에 사용)
            conversation_document = [Document(page_content=conversation_text)]

            # Step 3: 대화 내용 요약
            summarize_chain = load_summarize_chain(self.model, chain_type="map_reduce")
            summary_result = await summarize_chain.ainvoke({"input_documents": conversation_document})

            # 결과가 dict일 경우 처리
            summary = (
                summary_result.get("text", "") if isinstance(summary_result, dict) else summary_result
            )
            print(f"[Summary] {summary}")

            # Step 4: 생존율 계산
            survival_template = (
                "다음 요약된 대화를 바탕으로 유저의 생존율을 계산하세요.\n"
                "요약된 대화: {summary}\n"
                "유저가 서바이벌 상황에서 생존할 확률을 %로 표현하세요. "
                "숫자만 반환하고 이유는 설명하지 마세요."
            )
            survival_prompt = PromptTemplate(input_variables=["summary"], template=survival_template)
            survival_chain = LLMChain(llm=self.model, prompt=survival_prompt)
            survival_rate_result = await survival_chain.ainvoke({"summary": summary})

            # dict 형태일 경우 "text" 키에서 생존율 추출
            if isinstance(survival_rate_result, dict):
                survival_rate_text = survival_rate_result.get("text", "").strip()
            else:
                survival_rate_text = survival_rate_result.strip()

            survival_rate = int(survival_rate_text.replace("%", ""))  # "75" → 75
            print(f"[Survival Rate] {survival_rate}%")

            # Step 5: 엔딩 스토리 생성
            system_template = (
                "You are a master storyteller concluding an epic narrative. "
                "Based on the conversation history provided, create a compelling ending to the story.\n"
                "Conversation history: {conversation_text}\n"
                "Conclude the story in Korean, keeping the response under 500 characters. "
                "No choices are needed, just a final closure to the narrative."
            )
            ending_prompt = ChatPromptTemplate.from_template(system_template)
            ending_chain = ending_prompt | self.model | self.parser
            ending_story_result = await ending_chain.ainvoke({"conversation_text": conversation_text})

            # 결과가 dict일 경우 처리
            ending_story = (
                ending_story_result.get("text", "") if isinstance(ending_story_result, dict) else ending_story_result
            )
            print(f"[Ending Story] Generated ending: {ending_story}")

            if not ending_story:
                raise ValueError("No ending generated.")

            # Step 6: 결과 반환
            return {
                "summary": summary.strip(),
                "survival_rate": survival_rate,
                "ending_story": ending_story.strip()
            }

        except Exception as e:
            print(f"[Ending Story ERROR] {str(e)}")
            raise Exception(f"Error generating ending story: {str(e)}")
