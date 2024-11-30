import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI 
from langchain.schema.output_parser import StrOutputParser
from schemas.story_class import StoryGenerationRequest

load_dotenv()

class StoryGenerator:
    def __init__(self, api_key: str = os.getenv("OPENAI_KEY")):
        self.api_key = api_key
        self.model = ChatOpenAI(openai_api_key=self.api_key,
                                model="gpt-4o-mini",
                                temperature=0.2,
                                max_tokens=300)
        self.parser = StrOutputParser()

    async def generate_story(self, request: StoryGenerationRequest) -> str:
        try:
            genre = request.genre
            prompt = request.initialStory
            user_input = request.userInput
            conversation_history = request.conversationHistory or ""

            system_template = (
                f"You are an expert in storytelling. "
                f"Generate a story in the '{genre}' genre based on the following prompt: {prompt}."
            )
            if conversation_history:
                system_template += f"\nPrevious conversation: {conversation_history}"
            if user_input:
                system_template += f"\n\nThe user input: {user_input}. Continue the story accordingly."

            prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])

            chain = prompt_template | self.model | self.parser
            result = await chain.ainvoke({"genre": genre, "prompt": prompt})

            return result

        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")
