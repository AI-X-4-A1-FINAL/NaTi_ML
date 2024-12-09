#service/story_service.py

from typing import Dict
from models.story_generator import StoryGenerator
from schemas.story_class import StoryGenerationChatRequest

class StoryService:
    def __init__(self, story_generator: StoryGenerator):
       self.story_generator = story_generator
       self.active_stories: Dict[str, StoryGenerator] = {}

    async def generate_initial_story(self, genre: str) -> dict:
       try:
           # StoryGenerator에서 이미 파싱된 결과를 반환받음
           result = await self.story_generator.generate_initial_story(genre)
           
        #    print(f"서비스: {result}")  # 결과 로그
           # result는 이미 파싱된 딕셔너리 형태
           return {
               "story": result["story"],
               "choices": result["choices"],
               "file_name": result["file_name"] 
           }

       except Exception as e:
           print(f"[Story Service] Error in generate_initial_story: {str(e)}")
           raise Exception(f"Error generating initial story: {str(e)}")

    async def continue_story(self, request: StoryGenerationChatRequest) -> dict:
        """
        스토리를 이어가는 서비스 로직
        """
        try:
            # 요청 데이터를 딕셔너리로 변환
            request_dict = {
                "genre": request.genre,
                "user_choice": request.user_choice,
                "game_id": request.game_id
            }
            print(f"[Story Service] Received continue story request: {request_dict}")

            # StoryGenerator를 호출하여 결과를 반환받음
            result = await self.story_generator.continue_story(request_dict)

            # 결과 딕셔너리를 반환
            response = {
                "story": result.get("story", ""),  # 결과에 스토리가 없을 경우 빈 문자열 반환
                "choices": result.get("choices", []),  # 결과에 선택지가 없을 경우 빈 리스트 반환
                "game_id": result.get("game_id", request.game_id)  # 반환된 game_id 없으면 기존 요청 ID 사용
            }
            print(f"[Story Service] Generated story continuation: {response}")
            return response

        except KeyError as e:
            print(f"[Story Service] Missing key in response: {str(e)}")
            raise Exception(f"Missing key in story continuation response: {str(e)}")
        except Exception as e:
            print(f"[Story Service] Error in continue_story: {str(e)}")
            raise Exception(f"Error continuing story: {str(e)}")
        
    async def generate_ending_story(self, game_id: str, user_choice: str) -> dict:
        """
        마지막 엔딩 스토리를 생성하는 서비스 로직
        """
        try:
            # 스토리 히스토리를 메모리에서 가져옴
            story_history = self.story_generator.memory.load_memory_variables({}).get("history", [])
            if not story_history:
                raise ValueError(f"No story history found for the given game_id: {game_id}.")

            print(f"[Story Service] Generating ending for game_id: {game_id} with user_choice: {user_choice}")

            # 마지막 유저 선택 저장
            self.story_generator.memory.save_context(
                {"input": user_choice},
                {"output": f"User's final choice was: {user_choice}"}
            )

            # 엔딩 스토리 생성
            result = await self.story_generator.generate_ending_story(story_history)
            
            # 모델에서 반환된 값에서 필요한 데이터를 추출하여 적절히 매핑
            response = {
                "story": result.get("ending_story", "No ending story generated."),
                "survival_rate": result.get("survival_rate", 0),  # 기본값 0
                "game_id": game_id
            }

            print(f"[Story Service] Generated ending story: {response}")
            return response

        except ValueError as e:
            print(f"[Story Service] Validation error: {str(e)}")
            raise Exception(f"Validation error in generate_ending_story: {str(e)}")
        except Exception as e:
            print(f"[Story Service] Error in generate_ending_story: {str(e)}")
            raise Exception(f"Error generating ending story: {str(e)}")
