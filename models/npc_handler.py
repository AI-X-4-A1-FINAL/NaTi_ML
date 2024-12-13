#models/npc_handler.py

from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from typing import Dict, List, Optional

class NPCHandler:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = ChatOpenAI(
            openai_api_key=self.api_key,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=300
        )
        self.parser = StrOutputParser()
        self.memory = ConversationBufferWindowMemory(k=5, return_messages=True)
        self.current_context = ""
        self.last_choice = None

    async def generate_greeting(self, story: str, choices: List[str]) -> str:
        """NPC 초기 인사말 생성"""
        try:
            story_context = f"현재 스토리: {story}\n선택지들: {', '.join(choices)}"
            
            npc_initial_template = (
                "당신은 플레이어의 신뢰할 수 있는 길잡이입니다. 다음 상황을 바탕으로 플레이어와 대화해주세요:\n"
                "{story_context}\n\n"
                "규칙:\n"
                "1. 상황의 심각성을 인지하되, 희망적인 태도를 보여주세요.\n"
                "2. 이전 대화와 선택의 맥락을 자연스럽게 이어가세요.\n"
                "3. 플레이어의 선택이 미칠 영향을 은근히 암시해주세요.\n"
                "4. 응답은 2-3문장으로 짧게 작성하세요.\n"
                "5. 플레이어의 궁금증을 자극하세요.\n"
                "6. 항상 존댓말로 작성해주세요."
            )
            
            prompt = ChatPromptTemplate.from_template(npc_initial_template)
            chain = prompt | self.model | self.parser
            
            greeting = await chain.ainvoke({
                "story_context": story_context
            })
            
            return greeting
        except Exception as e:
            raise Exception(f"Error generating NPC greeting: {str(e)}")

    async def provide_advice(self, story_context: str, choices: List[str]) -> Dict:
        """NPC 조언 및 생존율 제공"""
        try:
            memory_vars = self.memory.load_memory_variables({})
            conversation_history = memory_vars.get("history", [])
            formatted_choices = "\n".join([f"선택지 {i+1}: {choice}" for i, choice in enumerate(choices)])
            
            npc_advice_template = (
                "당신은 플레이어의 신뢰할 수 있는 조언자입니다.\n"
                "항상 존댓말로 작성해주세요.\n"
                "현재 상황: {story_context}\n\n"
                "이전 대화 맥락: {conversation_history}\n\n"
                "선택지들:\n{choices}\n\n"
                "규칙:\n"
                "1. 각 선택지의 잠재적 결과나 위험을 암시하세요.\n"
                "2. 생존율을 제시하고 간단한 이유를 덧붙이세요.\n"
                "3. 조언은 1-2문장으로 간단하게 작성하세요.\n"
                "출력 형식:\n"
                "선택지1=잠재적 결과를 암시하는 조언|생존율 XX%\n"
                "선택지2=잠재적 결과를 암시하는 조언|생존율 XX%\n"
                "선택지3=잠재적 결과를 암시하는 조언|생존율 XX%\n\n"
                "추가 코멘트: (결과에 대한 통찰)"
            )

            prompt = ChatPromptTemplate.from_template(npc_advice_template)
            chain = prompt | self.model | self.parser

            response = await chain.ainvoke({
                "story_context": story_context,
                "conversation_history": "\n".join(str(msg) for msg in conversation_history),
                "choices": formatted_choices
            })

            response_data = {}
            lines = response.strip().split("\n")
            additional_comment = ""
            
            for line in lines:
                if line.startswith("추가 코멘트:"):
                    additional_comment = line.replace("추가 코멘트:", "").strip()
                    continue

                if "선택지" in line and "=" in line and "|" in line:
                    choice_num = line[line.find("선택지")+3:line.find("=")]
                    content = line.split("=")[1]
                    advice, survival = content.split("|")
                    survival_rate = int(''.join(filter(str.isdigit, survival)))
                    
                    response_data[f"additionalProp{choice_num}"] = {
                        "advice": advice.strip(),
                        "survival_rate": survival_rate
                    }

            self.memory.save_context(
                {"input": formatted_choices},
                {"output": response}
            )

            return {
                "response": response_data,
                "additional_comment": additional_comment
            }

        except Exception as e:
            raise Exception(f"Error generating NPC advice: {str(e)}")

    def get_final_message(self) -> str:
        """NPC 마지막 메시지"""
        return "이야기가 끝났네요. 당신의 선택에 따라 모든 것이 달라졌습니다."
