# service/story_service.py

from typing import Dict, List
from models.story_generator import StoryGenerator
from schemas.story_class import StoryGenerationChatRequest

class StoryService:
    def __init__(self, story_generator: StoryGenerator):
        self.story_generator = story_generator
        self.active_stories: Dict[str, StoryGenerator] = {}

    async def generate_initial_story(self, genre: str) -> dict:
        try:
            result = await self.story_generator.generate_initial_story(genre)
            parts = result.split("\nChoices: ")
            story = parts[0].replace("Story: ", "").strip()
            choices = []
            
            if len(parts) > 1:
                choices_text = parts[1].strip("[]")
                choices = [choice.strip().split(". ", 1)[-1] 
                         for choice in choices_text.split(",")]
            
            return {
                "story": story,
                "choices": choices,
                "story_id": "temp-id"
            }
        except Exception as e:
            raise Exception(f"Error generating initial story: {str(e)}")

    async def continue_story(self, request: StoryGenerationChatRequest) -> dict:
        try:
            result = await self.story_generator.continue_story(str(request))
            parts = result.split("\nChoices: ")
            story = parts[0].replace("Story: ", "").strip()
            choices = []
            
            if len(parts) > 1:
                choices_text = parts[1].strip("[]")
                choices = [choice.strip().split(". ", 1)[-1] 
                         for choice in choices_text.split(",")]
            
            return {
                "story": story,
                "choices": choices,
                "story_id": request.story_id
            }
        except Exception as e:
            raise Exception(f"Error continuing story: {str(e)}")