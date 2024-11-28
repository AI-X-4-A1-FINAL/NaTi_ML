import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_KEY")

# LangChain 기반 스토리 생성 함수
def generate_story(genre: str, prompt: str) -> str:
    try:      
        # 프롬프트 정의 부분
        system_template = (
            "You are an expert in storytelling. "
            "Generate a story in the '{genre}' genre based on the following prompt: "
            "The world is set in a universe where {prompt}. "
            "Ensure that the story reflects the theme of the genre and incorporates the prompt elements."
        )
        user_template = "{prompt}"

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", user_template)
        ])

        # OpenAI 모델 초기화
        model = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.2
        )

        # Output Parser 정의
        parser = StrOutputParser()

        # 체인 생성
        chain = prompt_template | model | parser

        # 체인 실행
        result = chain.invoke({"genre": genre, "prompt": prompt})
        return result
    except Exception as e:
        raise Exception(f"Error generating story: {str(e)}")