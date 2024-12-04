from typing import Dict, List
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
           
           # result는 이미 파싱된 딕셔너리 형태
           return {
               "story": result["story"],
               "choices": result["choices"],
               "story_id": result["story_id"]
           }

       except Exception as e:
           print(f"[Story Service] Error in generate_initial_story: {str(e)}")
           raise Exception(f"Error generating initial story: {str(e)}")

   async def continue_story(self, request: StoryGenerationChatRequest) -> dict:
       try:
           # StoryGenerationChatRequest를 딕셔너리로 변환
           request_dict = {
               "genre": request.genre,
               "user_choice": request.user_choice,
               "story_id": request.story_id
           }
           
           # StoryGenerator에서 이미 파싱된 결과를 반환받음
           result = await self.story_generator.continue_story(request_dict)
           
           # result는 이미 파싱된 딕셔너리 형태
           return {
               "story": result["story"],
               "choices": result["choices"],
               "story_id": result["story_id"]
           }
           
       except Exception as e:
           print(f"[Story Service] Error in continue_story: {str(e)}")
           raise Exception(f"Error continuing story: {str(e)}")