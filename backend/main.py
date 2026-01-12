from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import uuid
import traceback

# IMPORT THE HYBRID RECOMMENDER
from app.hybrid_recommender import hybrid_recommender 
from app.recommender import content_recommender

app = FastAPI()

# --- ADD THIS BLOCK ---
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- GLOBAL DATA ---
programs_data = []

def clean_csv_data(df: pd.DataFrame) -> List[Dict]:
    """
    Adapts your specific CSV columns to what the AI needs.
    """
    print(f"DEBUG: Found CSV Columns: {df.columns.tolist()}")

    # 1. Map YOUR columns to INTERNAL names
    # internal_key : your_csv_column
    rename_map = {
        'course_title': 'name',
        'course_organization': 'provider',
        'course_Certificate_type': 'type',
        'course_rating': 'rating',
        'course_difficulty': 'difficulty',
        'course_students_enrolled': 'enrolled'
    }
    
    # Apply renaming
    df = df.rename(columns=rename_map)

    # 2. FILL MISSING DATA (Crucial to prevent crashes)
    
    # If 'tags' are missing, we create them from other columns
    # We combine Organization + Difficulty + Type to act as "tags"
    if 'tags' not in df.columns:
        print("⚠️ Generating 'tags' from course metadata...")
        df['tags'] = df.apply(lambda x: f"{x.get('provider','')} {x.get('difficulty','')} {x.get('type','')}", axis=1)

    # If 'description' is missing, use the Name and Tags as the description
    if 'description' not in df.columns:
        print("⚠️ Generating 'description' from title...")
        df['description'] = df['name'] + " - " + df['tags']

    # Ensure 'field' exists for the dropdown filter
    if 'field' not in df.columns:
        # Default everyone to 'General' so the filter doesn't break
        df['field'] = "General"
    
    # Ensure ID exists
    if 'id' not in df.columns:
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]

    # Clean text columns to be strings (no NaN)
    for col in ['name', 'tags', 'description', 'field']:
        df[col] = df[col].fillna("").astype(str)
        
    # 3. Create 'min_gpa' (randomized slightly for realism if missing)
    if 'min_gpa' not in df.columns:
        import random
        # Assign random GPAs between 60 and 90 for demo purposes
        df['min_gpa'] = [random.randint(60, 90) for _ in range(len(df))]

    # Return as list of dictionaries
    return df.to_dict(orient="records")

# --- LOAD DATA ON STARTUP ---
try:
    # Read CSV
    df = pd.read_csv("coursea_data.csv")
    
    # Clean Data
    programs_data = clean_csv_data(df)
    
    # Train AI Model immediately
    print("🔄 Training AI with cleaned data...")
    content_recommender.fit(programs_data)
    print(f"✅ Success! Loaded {len(programs_data)} courses.")
    
except Exception as e:
    print(f"❌ CRITICAL ERROR loading data: {e}")
    traceback.print_exc()
    programs_data = []

# --- INPUT SCHEMA ---
class StudentInput(BaseModel):
    name: str
    email: str
    field: str
    gpa: float
    interests: List[str]
    grades: Dict[str, float]

# --- ENDPOINT ---
@app.post("/recommend")
async def get_recommendations(student: StudentInput):
    try:
        if not programs_data:
            raise HTTPException(status_code=500, detail="Backend has no data loaded.")

        student_dict = student.dict()
        
        # Log for debugging
        print(f"🔍 Request for: {student_dict['name']} (Field: {student_dict['field']})")

        recommendations = hybrid_recommender.recommend(
            student_data=student_dict,
            programs=programs_data,
            top_k=5
        )

        return recommendations

    except Exception as e:
        print(f"SERVER ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "active", "courses_available": len(programs_data)}