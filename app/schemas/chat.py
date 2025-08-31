from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="OpenAI-style messages")

class Citation(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    chunk: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    source: Optional[str] = "model"
    citations: Optional[List[Citation]] = None
    usage_prompt_tokens: Optional[int] = None
    usage_completion_tokens: Optional[int] = None
    usage_total_tokens: Optional[int] = None
