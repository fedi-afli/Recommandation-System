from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- Shared Base Models ---

class StudentBase(BaseModel):
    name: str
    email: str
    interests: List[str]
    grades: Dict[str, Any]  # e.g. {"Math": 90, "Science": 85}

# --- Student Schemas ---

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: str

    class Config:
        from_attributes = True

# --- Recommendation Schemas ---

class RecommendationRequest(BaseModel):
    student_id: str
    top_k: int = 5

class RecommendationResponse(BaseModel):
    program_id: str
    program_name: str
    score: float
    explanation: str

# --- Feedback Schemas ---

class FeedbackCreate(BaseModel):
    student_id: str
    program_id: str
    clicked: bool = False
    accepted: bool = False
    rating: Optional[int] = None

class FeedbackResponse(BaseModel):
    message: str