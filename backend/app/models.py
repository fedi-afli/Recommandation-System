from sqlalchemy import Column, String, Float, Integer, JSON, Boolean, ForeignKey
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True) 
    interests = Column(JSON) 
    grades = Column(JSON)

class Program(Base):
    __tablename__ = "programs"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    tags = Column(JSON)
    skills = Column(JSON)      
    requirements = Column(JSON)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    program_id = Column(String, ForeignKey("programs.id")) # Changed to ID link
    program_name = Column(String)
    score = Column(Float)
    explanation = Column(String)

# NEW TABLE: This stores what users actually liked/clicked
class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    program_id = Column(String, ForeignKey("programs.id"))
    clicked = Column(Boolean, default=False)
    accepted = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True) # 1-5 stars