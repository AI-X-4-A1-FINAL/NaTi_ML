import os
import random
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import logging

# 환경 변수 로드
load_dotenv()

# LangChain 구성
openai_key = os.getenv("OPENAI_KEY")
if not openai_key:
    raise ValueError("OPENAI_KEY 환경 변수를 설정해주세요.")

llm = ChatOpenAI(
    temperature=0.4,
    model="gpt-4o-mini",
    openai_api_key=openai_key
)
memory = ConversationBufferMemory(return_messages=True)

class StoryGenerator:
    def __init__(self, prompt_base_path: str):
        self.llm = llm
        self.memory = memory
        self.prompt_base_path = prompt_base_path  # prompts 폴더 경로

    def read_prompt(self, genre: str) -> str:
        """장르 기반으로 프롬프트를 읽어오는 함수."""
        genre_path = os.path.join(self.prompt_base_path, genre)

        if not os.path.exists(genre_path):
            raise FileNotFoundError(f"Genre folder '{genre}' not found at {genre_path}.")

        txt_files = [f for f in os.listdir(genre_path) if f.endswith(".txt")]
        if not txt_files:
            raise FileNotFoundError(f"No prompt files found in genre folder '{genre}'.")

        selected_file = random.choice(txt_files)
        file_path = os.path.join(genre_path, selected_file)

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    async def generate_initial_story(self, genre: str) -> str:
        """장르와 로컬 프롬프트를 기반으로 세계관 생성."""
        try:
            prompt = self.read_prompt(genre)

            # 시스템 템플릿 구성
            system_template = (
                f"You have to print it out in Korean. You are a storyteller. Generate a story in the '{genre}' genre using the following prompt: {prompt}."
            )
            prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])

            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            story = chain.run({"genre": genre, "prompt": prompt})

            # 생성된 스토리를 메모리에 추가
            self.memory.chat_memory.add_message({"role": "system", "content": story})
            return story

        except Exception as e:
            logging.error(f"Error generating story: {e}")
            raise Exception(f"Error generating story: {str(e)}")
