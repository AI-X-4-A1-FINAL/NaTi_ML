from typing import Dict, Optional
from models.s3_manager import S3Manager

class StoryTemplates:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.s3_manager = S3Manager()
        return cls._instance

    async def get_template(self, genre: str, type_: str, base_prompt: str = None) -> str:
        """통합된 템플릿 가져오기 메서드"""
        template = await self.s3_manager.get_genre_type_template(genre, type_)
        content = template.get("content", "")
        
        if base_prompt and type_ in ["initial", "continue"]:
            return f"{content}\n{base_prompt}"
        return content

# 싱글톤 인스턴스 생성
_templates = StoryTemplates()

# 외부에서 사용할 비동기 함수들
async def get_default_npc_template(story_context: str) -> str:
    """
    기본 NPC 템플릿을 story_context로 포맷하여 반환
    """
    template = await _templates.get_template("default", "npc")
    return template.format(story_context=story_context)


async def get_default_advice_template(story_context: str, conversation_history: str, choices: str) -> str:
    """
    기본 Advice 템플릿을 story_context, conversation_history, choices로 포맷하여 반환
    """
    template = await _templates.get_template("default", "advice")
    return template.format(
        story_context=story_context,
        conversation_history=conversation_history,
        choices=choices
    )

async def get_romance_initial_template(base_prompt: str) -> str:
    return await _templates.get_template("romance", "initial", base_prompt)

async def get_survival_initial_template(base_prompt: str) -> str:
    return await _templates.get_template("survival", "initial", base_prompt)

async def get_romance_continue_template(stage_template: str, previous_story: str, user_choice: str) -> str:
    template = await _templates.get_template("romance", "continue")
    return template.format(
        stage_template=stage_template,
        previous_story=previous_story,
        user_choice=user_choice
    )

async def get_survival_continue_template(stage_template: str, previous_story: str, user_choice: str) -> str:
    template = await _templates.get_template("survival", "continue")
    return template.format(
        stage_template=stage_template,
        previous_story=previous_story,
        user_choice=user_choice
    )

# 엔딩 템플릿 수정
async def get_romance_ending_template(conversation_text: str, summary: str) -> str:
    template = await _templates.get_template("romance", "ending")
    return template.format(
        conversation_text=conversation_text,
        summary=summary
    )

async def get_survival_ending_template(conversation_text: str, summary: str) -> str:
    template = await _templates.get_template("survival", "ending")
    return template.format(
        conversation_text=conversation_text,
        summary=summary
    )

# 생존율 템플릿 수정
async def get_survival_rate_template(summary: str) -> str:
    template = await _templates.get_template("survival", "rate")
    return template.format(summary=summary)

async def get_romance_rate_template(summary: str) -> str:
    template = await _templates.get_template("romance", "rate")
    return template.format(summary=summary)
