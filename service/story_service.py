from core.s3_manager import S3Manager 
from models.story_generator import StoryGenerator
from schemas.story_class import StoryGenerationStartRequest, StoryGenerationChatRequest

class StoryService:
    def __init__(self, s3_manager, story_generator: StoryGenerator):
        self.s3_manager = s3_manager
        self.story_generator = story_generator

    async def generate_initial_story(self, genre: str, tags: list) -> str:
        request = StoryGenerationStartRequest(genre=genre, tags=tags)
        return await self.story_generator.generate_initial_story(request)

    async def continue_story(self, genre: str, initial_story: str, user_input: str, conversation_history: list) -> str:
        request = StoryGenerationChatRequest(
            genre=genre, 
            initialStory=initial_story, 
            userInput=user_input, 
            conversationHistory=conversation_history
        )
        return await self.story_generator.continue_story(request)