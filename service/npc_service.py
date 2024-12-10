# service/npc_service.py
from typing import Dict
from models.story_generator import StoryGenerator
from schemas.story_class import NPCResponse, NPCChatRequest

class NPCService:
    def __init__(self, story_generator: StoryGenerator):
        self.story_generator = story_generator

    # service/npc_service.py

from typing import Dict
from models.story_generator import StoryGenerator
from models.npc_handler import NPCHandler
from schemas.story_class import NPCResponse, NPCChatRequest

class NPCService:
    def __init__(self, story_generator: StoryGenerator, npc_handler: NPCHandler):
        self.story_generator = story_generator
        self.npc_handler = npc_handler  # NPCHandler 인스턴스를 직접 받음

    async def get_npc_advice(self, game_id: str) -> str:
        """NPC 조언 얻기"""
        try:
            # 스토리 컨텍스트 가져오기
            story_context = self.story_generator.story_memory.load_memory_variables({})
            history = story_context.get("history", [])
            
            if not history:
                raise ValueError(f"No story context found for game_id: {game_id}")

            # 마지막 컨텍스트에서 스토리와 선택지 추출
            last_message = history[-1].content if hasattr(history[-1], "content") else str(history[-1])
            
            if "Story:" not in last_message or "Choices:" not in last_message:
                raise ValueError("Invalid story format in context")

            story_part = last_message.split("Story:")[1].split("Choices:")[0].strip()
            choices_part = last_message.split("Choices:")[1].strip("[] \n").split(",")
            choices = [choice.strip() for choice in choices_part]

            # NPC 인사말 생성
            npc_message = await self.npc_handler.generate_greeting(story_part, choices)
        
            return {
                "npc_message": npc_message,
                "game_id": game_id
            }

        except Exception as e:
            print(f"[NPC Service] Error in get_npc_advice: {str(e)}")
            raise Exception(f"Error getting NPC advice: {str(e)}")

    async def chat_with_npc(self, game_id: str) -> NPCResponse:
        """NPC가 선택지에 대한 조언과 생존율 제공"""
        try:
            # 스토리 컨텍스트 가져오기
            story_context = self.story_generator.story_memory.load_memory_variables({})
            history = story_context.get("history", [])
            
            if not history:
                raise ValueError(f"No story context found for game_id: {game_id}")

            # 마지막 컨텍스트에서 스토리와 선택지 추출
            last_message = history[-1].content if hasattr(history[-1], "content") else str(history[-1])
            
            if "Story:" not in last_message or "Choices:" not in last_message:
                raise ValueError("Invalid story format in context")

            story_part = last_message.split("Story:")[1].split("Choices:")[0].strip()
            choices_part = last_message.split("Choices:")[1].strip("[] \n").split(",")
            choices = [choice.strip() for choice in choices_part]

            # NPC 핸들러를 통해 직접 조언 얻기
            advice = await self.npc_handler.provide_advice(story_part, choices)
        
            return NPCResponse(
                response=advice["response"],
                game_id=game_id,
                additional_comment=advice.get("additional_comment")
            )

        except Exception as e:
            print(f"[NPC Service] Error in chat_with_npc: {str(e)}")
            raise Exception(f"Error in NPC chat: {str(e)}")