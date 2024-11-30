from core.s3_manager import S3Manager 
from models.story_generator import StoryGenerator

class StoryService:
    def __init__(self, s3_manager: S3Manager, story_generator: StoryGenerator):
        self.s3_manager = s3_manager
        self.story_generator = story_generator

    async def generate_initial_story(self, genre: str, tags: list):
        prompt = await self.s3_manager.get_random_prompt(genre)
        modified_prompt = f"{prompt}\n\nTags: {', '.join(tags)}"
        return await self.story_generator.generate_story(genre, modified_prompt)

    async def continue_story(self, genre: str, initial_story: str, user_input: str, conversation_history: list):
        conversation_text = "\n".join(conversation_history) if conversation_history else ""
        return await self.story_generator.generate_story(genre, initial_story, user_input, conversation_text)
