from pydantic import BaseModel
from typing import List, Optional

class StoryGenerationStartRequest(BaseModel):
    genre: str
    tags: Optional[List[str]] = []

class StoryGenerationChatRequest(BaseModel):
    genre: str
    tags: Optional[List[str]] = []
    currentStage: Optional[int] = 1
    initialStory: Optional[str] = ""
    userInput: Optional[str] = ""
    previousUserInput: Optional[str] = ""
    conversationHistory: Optional[List[str]] = None
