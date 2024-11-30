import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI  
from langchain.schema.output_parser import StrOutputParser
from schemas.story_class import StoryGenerationStartRequest, StoryGenerationChatRequest

load_dotenv()

class StoryGenerator:
    def __init__(self, api_key: str = os.getenv("OPENAI_KEY")):
        self.api_key = api_key
        self.model = ChatOpenAI(openai_api_key=self.api_key, 
                                model="gpt-4o-mini",
                                temperature=0.2,
                                max_tokens=300)
        self.parser = StrOutputParser()

    # /start 엔드포인트
    async def generate_initial_story(self, request: StoryGenerationStartRequest) -> str:
        try:
            genre = request.genre
            tags = request.tags

            system_template = (
                f"You are an expert in storytelling. "
                f"Generate a story in the '{genre}' genre based on the following tags: {tags}."
            )

            prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])

            chain = prompt_template | self.model | self.parser
            result = await chain.ainvoke({"genre": genre, "tags": tags})

            return result

        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")

    # /chat 엔드포인트
    async def continue_story(self, request: StoryGenerationChatRequest) -> str:
        try:
            genre = request.genre
            initial_story = request.initialStory
            user_input = request.userInput
            conversation_history = request.conversationHistory or ""

            system_template = (
                f"You are an expert in storytelling. "
                f"Continue the story in the '{genre}' genre based on the following initial story: {initial_story}."
            )
            if conversation_history:
                system_template += f"\nPrevious conversation: {conversation_history}"
            if user_input:
                system_template += f"\n\nThe user input: {user_input}. Continue the story accordingly."

            prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])

            chain = prompt_template | self.model | self.parser
            result = await chain.ainvoke({
                "genre": genre, 
                "initial_story": initial_story,
                "user_input": user_input,
                "conversation_history": conversation_history
            })

            return result

        except Exception as e:
            raise Exception(f"Error continuing story: {str(e)}")
