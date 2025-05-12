from pydantic import BaseModel
from typing import Optional

class StoryRequest(BaseModel):
    theme: Optional[str] = None
    genre: Optional[str] = None
    characters: Optional[int] = 1
    length: str = "medium"  # short, medium, long
    temperature: float = 0.7
    maxTokens: int = 1000

class StoryResponse(BaseModel):
    title: str
    story: str