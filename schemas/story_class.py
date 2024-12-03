from pydantic import BaseModel
from typing import List, Optional, Union

class StoryGenerationStartRequest(BaseModel):
    genre: str
    # tags: Optional[List[str]] = []
    # prompt: str

class StoryGenerationChatRequest(BaseModel):
    genre: str
    tags: Optional[List[str]] = []
    currentStage: Optional[int] = 1
    initialStory: Optional[str] = ""
    userInput: Optional[str] = ""
    previousUserInput: Optional[str] = ""
    conversationHistory: Union[List[str], str] = []
