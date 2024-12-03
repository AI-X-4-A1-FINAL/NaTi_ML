import os
import random
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Tuple, List
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import logging

# 환경 변수 로드
load_dotenv()

# 데이터 모델 정의
class StoryGenerationChatRequest(BaseModel):
    genre: str
    initialStory: str
    userInput: str
    conversationHistory: Optional[str] = None

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

    async def generate_initial_story(self, genre: str) -> Tuple[str, List[str]]:
        """장르와 로컬 프롬프트를 기반으로 세계관 생성."""
        try:
            logging.info(f"Starting story generation for genre: {genre}")
            prompt = self.read_prompt(genre)
            logging.info(f"Prompt successfully loaded: {prompt}")

            # 시스템 템플릿 구성
            system_template = (
                f"You have to print it out in Korean. You are a storyteller. Generate a story in the '{genre}' genre using the following prompt: {prompt}.\n"
                "The output must include:\n"
                "1. A short story (200-300 words).\n"
                "2. Three concise and distinct choices for the user to shape the story.\n\n"
                "Format:\n"
                "Story: [Generated story text]\n"
                "Choices: [1. Choice 1, 2. Choice 2, 3. Choice 3]"
            )
            prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])
            chain = prompt_template | self.llm

            response = await chain.ainvoke({"genre": genre, "prompt": prompt})

            logging.info(f"Model response content: {response.content}")

            # 스토리와 선택지 파싱
            story, choices = self.parse_story_and_choices(response)

            logging.info(f"Parsed story: {story}")
            logging.info(f"Parsed choices: {choices}")

            return story, choices

        except Exception as e:
            logging.error(f"Error generating story: {e}")
            raise Exception(f"Error generating story: {str(e)}")


    async def continue_story(self, request: StoryGenerationChatRequest) -> Tuple[str, List[str]]:
        """사용자의 입력을 기반으로 스토리 진행."""
        try:
            genre = request.genre
            initial_story = request.initialStory
            user_input = request.userInput
            conversation_history = request.conversationHistory or ""

            # 시스템 템플릿 구성
            system_template = (
                f"You are an expert storyteller. "
                f"Continue the story in the '{genre}' genre based on the following initial story: {initial_story}.\n"
                f"User input: {user_input}\n"
                f"Conversation history: {conversation_history}\n\n"
                "The output must include:\n"
                "1. The continuation of the story (200-300 words).\n"
                "2. Exactly three concise and distinct choices for the user to shape the story further.\n\n"
                "Ensure the output is formatted as follows:\n"
                "Story: [Generated story text]\n"
                "Choices: [1. Choice 1, 2. Choice 2, 3. Choice 3]"
            )
            prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])

            chain = prompt_template | self.llm
            response = await chain.ainvoke({
                "genre": genre,
                "initial_story": initial_story,
                "user_input": user_input,
                "conversation_history": conversation_history
            })

            # 스토리와 선택지 파싱
            story, choices = self.parse_story_and_choices(response)

            # 생성된 스토리를 메모리에 추가
            self.memory.chat_memory.add_message({"role": "user", "content": user_input})
            self.memory.chat_memory.add_message({"role": "system", "content": story})

            return story, choices

        except Exception as e:
            logging.error(f"Error continuing story: {e}")
            raise Exception(f"Error continuing story: {str(e)}")

    def parse_story_and_choices(self, response: "AIMessage") -> Tuple[str, List[str]]:
        """스토리와 선택지를 파싱."""
        try:
            # 응답에서 content 추출
            content = response.content
            logging.debug(f"Response content for parsing: {content}")

            # Story와 Choices 분리
            if "Choices:" in content:
                parts = content.split("Choices:")
                story = parts[0].strip().replace("Story:", "").strip()
                choices = [choice.strip() for choice in parts[1].split(",") if choice.strip()]
            else:
                # Choices 키워드가 없을 경우 기본값 생성
                story = content.strip()
                choices = ["Option 1: Placeholder", "Option 2: Placeholder", "Option 3: Placeholder"]

            # 선택지가 부족하면 기본값 추가
            if len(choices) < 3:
                logging.warning("Insufficient choices generated. Adding placeholder choices.")
                choices += [f"Option {i + 1}: Placeholder choice" for i in range(3 - len(choices))]

            return story, choices
        except Exception as e:
            raise ValueError(f"Failed to parse story and choices: {e}")


