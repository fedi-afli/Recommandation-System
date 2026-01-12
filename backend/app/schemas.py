from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class StudentBase(BaseModel):
    name: str
    email: str
    interests: List[str]
    grades: Dict[str, Any]  


class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: str

    class Config:
        from_attributes = True



class RecommendationRequest(BaseModel):
    student_id: str
    top_k: int = 5

class RecommendationResponse(BaseModel):
    program_id: str
    program_name: str
    score: float
    explanation: str



class FeedbackCreate(BaseModel):
    student_id: str
    program_id: str
    clicked: bool = False
    accepted: bool = False
    rating: Optional[int] = None

class FeedbackResponse(BaseModel):
    message: str