import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI



# 환경 변수 가져와
load_dotenv()

# OpenAI API 키
api_key = os.getenv("OPENAI_KEY")

# 제발 재밌게 만들어줘
def generate_story(genre: str, prompt: str, user_input: str = None, conversation_history: str = "") -> str:
    try:
        # 기본적인 프롬프트 템플릿
        system_template = (
            "You are an expert in storytelling. "
            "Generate a story in the '{genre}' genre based on the following prompt: "
            "The world is set in a universe where {prompt}. "
            "Ensure that the story reflects the theme of the genre and incorporates the prompt elements."
        )
        
        # 대화 내용이 있을 경우, 대화 내역을 포함한 스토리 진행
        if conversation_history:
            conversation_part = f"\nPrevious conversation:\n{conversation_history}"
        else:
            conversation_part = ""
        
        # 유저 입력이 있을 경우, 그에 맞는 이야기를 이어나가도록 프롬프트 구성
        if user_input:
            system_template += f"\n\nThe user input: {user_input}. Continue the story accordingly."

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template + conversation_part),
            ("user", "{prompt}")
        ])

        # OpenAI 모델 초기화
        model = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=200
        )

        # Output Parser 정의
        parser = StrOutputParser()

        # LangChain 체인 생성
        chain = prompt_template | model | parser

        # 체인 실행
        result = chain.invoke({"genre": genre, "prompt": prompt})

        # 생성된 스토리 반환
        return result
    except Exception as e:
        raise Exception(f"Error generating story: {str(e)}")