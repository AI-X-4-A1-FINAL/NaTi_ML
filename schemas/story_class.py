# schemas/story_class.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

class ChoiceAdvice(BaseModel):
    advice: str
    survival_rate: int  # spring에서 JsonProperty로 매핑

class StoryGenerationStartRequest(BaseModel):
    genre: str = Field(..., description="Story genre")
    tags: List[str] = Field(default=list(), description="Story tags")

class StoryGenerationChatRequest(BaseModel):
    genre: str = Field(..., description="Story genre")
    user_choice: str = Field(..., description="User's selected choice")  # user_select -> user_choice
    game_id: str = Field(..., description="Story session ID")

class NPCChatRequest(BaseModel):
    game_id: str = Field(..., description="Game session ID")

class StoryResponse(BaseModel):
    story: str = Field(..., description="Generated story text")
    choices: List[str] = Field(..., description="Available choices")
    file_name: Optional[str] = Field(None, description="File name")

class NPCResponse(BaseModel):
    response: Dict[str, ChoiceAdvice]
    game_id: str
    additional_comment: Optional[str] = None

class StoryEndRequest(BaseModel):
    game_id: str = Field(..., description="Game session ID")
    genre: str = Field(..., description="Story genre")
    user_choice: str = Field(..., description="User's final choice")

class StoryEndResponse(BaseModel):
    story: str = Field(..., description="Final story")
    survival_rate: int = Field(..., description="Survival rate percentage")
    game_id: str = Field(..., description="Game session ID")
    npc_final_message: Optional[str] = Field(None, description="NPC's final message")

class NPCAdviceResponse(BaseModel):
    npc_message: str
    game_id: str