# schemas/story_class.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

class ChoiceAdvice(BaseModel):
    advice: str
    survival_rate: int

class StoryGenerationStartRequest(BaseModel):
    genre: str = Field(..., description="Story genre")

class StoryGenerationChatRequest(BaseModel):
    genre: str = Field(..., description="Story genre")
    user_choice: str = Field(..., description="User's selected choice (1, 2, or 3)")
    game_id: str = Field(..., description="Story session ID")

class NPCChatRequest(BaseModel):
    game_id: str = Field(..., description="Game session ID")

class StoryResponse(BaseModel):
    story: str = Field(..., description="Generated story text")
    choices: List[str] = Field(..., description="Available choices")


class NPCResponse(BaseModel):
    response: Dict[str, ChoiceAdvice]
    game_id: str
    additional_comment: Optional[str] = None

class StoryEndRequest(BaseModel):
    game_id: str = Field(..., description="Game session ID")
    user_choice: str = Field(..., description="User's final choice")

class StoryEndResponse(BaseModel):
    story: str = Field(..., description="Final story")
    survival_rate: int = Field(..., description="Survival rate percentage")
    game_id: str = Field(..., description="Game session ID")
    npc_final_message: Optional[str] = Field(None, description="NPC's final message")

class NPCAdviceResponse(BaseModel):
    npc_message: str
    game_id: str