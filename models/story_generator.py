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
        
    async def generate_initial_story(self, genre: str) -> Dict[str, str]:
        try:
            self.story_id = str(uuid.uuid4())
            print(f"[Initial Story] Generated new story_id: {self.story_id}")
            
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
            
            conversation_history = self.memory.load_memory_variables({}).get("history", [])
            print(f"[Continue Story] Current conversation history: {conversation_history}")
            
            system_template = (
                "You are a master storyteller continuing an ongoing narrative. "
                "Based on the previous context and user's choice, continue the story.\n"
                "Previous context: {conversation_history}\n"
                "User input: {user_input}\n"
                "Continue the story in Korean, keeping response under 500 characters. "
                "End with exactly 3 new choices. Format: 'Story: [text]\nChoices: [1,2,3]'"
            )
            
            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser
            
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

            self.memory.save_context({"input": request.get("user_choice", "")}, {"output": result})
            
            return {
                "story": story,
                "choices": choices,
                "story_id": self.story_id
            }

        except Exception as e:
            print(f"[Continue Story] ERROR: {str(e)}")
            print(f"[Continue Story] Error type: {type(e)}")
            print(f"[Continue Story] Full error details: {e.__dict__}")
            raise Exception(f"Error continuing story: {str(e)}")
