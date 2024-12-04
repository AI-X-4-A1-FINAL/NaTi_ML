import os
from typing import Optional
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory

load_dotenv()

class StoryGenerator:
    def __init__(self, api_key: Optional[str] = None, s3_manager=None):
        self.api_key = api_key or os.getenv("OPENAI_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.s3_manager = s3_manager
        self.model = ChatOpenAI(
            openai_api_key=self.api_key,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=500
        )
        self.parser = StrOutputParser()
        self.memory = ConversationBufferWindowMemory(k=5, return_messages=True)

    async def generate_initial_story(self, genre: str) -> str:
        try:
            # S3에서 프롬프트 가져오기
            base_prompt = await self.s3_manager.get_random_prompt(genre)
            
            system_template = (
                "You are a master storyteller specializing in narrative creation. "
                f"{base_prompt}\n"
                "The story should be written in Korean, maintaining proper narrative flow "
                "and cultural context. Keep the response under 500 characters. "
                "End with exactly 3 survival choices. Format: 'Story: [text]\nChoices: [1,2,3]'"
            )

            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser  # RunnableSequence-style chain

            result = await chain.ainvoke({})
            
            if not result:
                raise ValueError("No story generated.")
            
            self.memory.save_context({"input": "Story begins"}, {"output": result})
            return result.strip()

        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")

    async def continue_story(self, request_str: str) -> str:
        try:
            conversation_history = self.memory.load_memory_variables({}).get("history", [])
            
            system_template = (
                "You are a master storyteller continuing an ongoing narrative. "
                "Based on the previous context and user's choice, continue the story.\n"
                "Previous context: {conversation_history}\n"
                "User input: {user_input}\n"
                "Continue the story in Korean, keeping response under 500 characters. "
                "End with exactly 3 new choices. Format: 'Story: [text]\nChoices: [1,2,3]'"
            )

            prompt_template = ChatPromptTemplate.from_template(system_template)
            chain = prompt_template | self.model | self.parser  # RunnableSequence-style chain

            result = await chain.ainvoke({
                "conversation_history": conversation_history,
                "user_input": request_str
            })

            if not result:
                raise ValueError("No continuation generated.")

            self.memory.save_context({"input": request_str}, {"output": result})
            return result.strip()

        except Exception as e:
            raise Exception(f"Error continuing story: {str(e)}")
