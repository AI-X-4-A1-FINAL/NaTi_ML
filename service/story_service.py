from models.story_generator import StoryGenerator

class StoryService:
    def __init__(self, story_generator: StoryGenerator):
        self.story_generator = story_generator

    async def generate_initial_story(self, genre: str) -> str:
        """StoryGenerator를 호출하여 초기 스토리를 생성."""
        return await self.story_generator.generate_initial_story(genre)
