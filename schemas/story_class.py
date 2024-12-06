# schemas/story_class.py

from pydantic import BaseModel, Field
from typing import List, Optional

class StoryGenerationStartRequest(BaseModel):
    genre: str = Field(..., description="Story genre")

class StoryGenerationChatRequest(BaseModel):
    genre: str = Field(..., description="Story genre")
    user_choice: str = Field(..., description="User's selected choice (1, 2, or 3)")
    game_id: str = Field(..., description="Game session ID")
    
class StoryResponse(BaseModel):
    story: str = Field(..., description="Generated story text")
    choices: List[str] = Field(..., description="Available choices")

class StoryEndRequest(BaseModel):
    game_id: str = Field(..., description="Story session ID")