from typing import List, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    question: str
    answer: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[int] = None

class MessageState(BaseModel):
    intro_message: Optional[str] = Field(
        None, description="Introduction text shown before the first question"
    )
    questions: List[str] = Field(default_factory=list, description="List of interview questions")
    messages: List[Message] = Field(default_factory=list, description="Interview Q/A messages")
    final_feedback: Optional[str] = Field(None, description="Overall feedback")
    final_score: Optional[int] = Field(None, description="Overall score")
    final_recommendation: Optional[str] = Field(None, description="Final recommendation")
    outro_message: Optional[str] = Field(
        None, description="Closing text shown after the summary"
    )

