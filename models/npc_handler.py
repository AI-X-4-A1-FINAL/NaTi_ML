from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from templates.story_templates import get_default_npc_template, get_default_advice_template
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
            
            default_npc_template = get_default_npc_template()
            prompt = ChatPromptTemplate.from_template(default_npc_template)
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
            
            default_advice_template = get_default_advice_template()
            prompt = ChatPromptTemplate.from_template(default_advice_template)
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
