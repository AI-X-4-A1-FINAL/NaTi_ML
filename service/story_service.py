# service/story_service.py
from typing import List, Dict, Optional, Union
from models.story_generator import StoryGenerator
from models.npc_handler import NPCHandler  # NPCHandler import 추가
from service.npc_service import NPCService
from schemas.story_class import (
    StoryGenerationChatRequest,
    NPCChatRequest,
    NPCResponse
)

class StoryService:
    def __init__(self, story_generator: StoryGenerator):
        self.story_generator = story_generator
        self.active_stories: Dict[str, StoryGenerator] = {}
        self.npc_handler = NPCHandler(api_key=story_generator.api_key)  # NPCHandler를 직접 초기화
        self.npc_service = NPCService(story_generator=story_generator, npc_handler=self.npc_handler)  # npc_handler 전달

    async def generate_initial_story(self, genre: str) -> dict:
        try:
            result = await self.story_generator.generate_initial_story(genre)
            return {
                "story": result["story"],
                "choices": result["choices"],
                "file_name": result["file_name"]
            }
        except Exception as e:
            print(f"[Story Service] Error in generate_initial_story: {str(e)}")
            raise Exception(f"Error generating initial story: {str(e)}")

    async def continue_story(self, request: StoryGenerationChatRequest) -> dict:
        try:
            request_dict = {
                "genre": request.genre,
                "user_choice": request.user_choice,
                "game_id": request.game_id
            }
            print(f"[Story Service] Received continue story request: {request_dict}")

            result = await self.story_generator.continue_story(request_dict)

            response = {
                "story": result.get("story", ""),
                "choices": result.get("choices", []),
                "game_id": result.get("game_id", request.game_id)
            }
            print(f"[Story Service] Generated story continuation: {response}")
            return response

        except KeyError as e:
            print(f"[Story Service] Missing key in response: {str(e)}")
            raise Exception(f"Missing key in story continuation response: {str(e)}")
        except Exception as e:
            print(f"[Story Service] Error in continue_story: {str(e)}")
            raise Exception(f"Error continuing story: {str(e)}")

    async def chat_with_npc(self, game_id: str) -> NPCResponse:
        """NPC 서비스를 통한 NPC 응답 얻기"""
        return await self.npc_service.chat_with_npc(game_id)

    async def generate_ending_story(self, game_id: str, user_choice: str) -> dict:
        """엔딩 스토리 생성"""
        try:
            story_history = self.story_generator.story_memory.load_memory_variables({}).get("history", [])
            if not story_history:
                raise ValueError(f"No story history found for game_id: {game_id}")

            print(f"[Story Service] Generating ending for game_id: {game_id} with user_choice: {user_choice}")

            self.story_generator.story_memory.save_context(
                {"input": user_choice},
                {"output": f"User's final choice was: {user_choice}"}
            )

            result = await self.story_generator.generate_ending_story(story_history)

            response = {
                "story": result.get("ending_story", "No ending story generated."),
                "survival_rate": result.get("survival_rate", 0),
                "game_id": game_id,
                "npc_final_message": result.get("npc_final_message")
            }

            return response

        except ValueError as e:
            print(f"[Story Service] Validation error: {str(e)}")
            raise Exception(f"Validation error in generate_ending_story: {str(e)}")
        except Exception as e:
            print(f"[Story Service] Error in generate_ending_story: {str(e)}")
            raise Exception(f"Error generating ending story: {str(e)}")