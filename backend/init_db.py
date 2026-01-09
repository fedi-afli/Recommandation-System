import pandas as pd
import json
from app.database import engine, Base, SessionLocal
from app.models import Program, Student, Feedback, Recommendation
import uuid

def init_db():
    print("🔄 Resetting Database...")
    
    # 1. Drop old tables and create new ones
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    try:
        # 2. Load your specific CSV file
        csv_file = "coursea_data.csv" 
        print(f"📂 Loading data from {csv_file}...")
        
        df = pd.read_csv(csv_file)
        
        # 3. Map Coursera Columns to our App's Schema
        # We need: name, description, tags (as a list)
        
        programs_to_add = []
        
        for index, row in df.iterrows():
            # Create a synthetic description since the CSV doesn't have one
            # Example: "A Beginner level course by University of Pennsylvania."
            syn_description = f"A {row['course_difficulty']} level {row['course_Certificate_type']} provided by {row['course_organization']}."
            
            # Combine useful attributes into tags
            # We filter out 'nan' values just in case
            tags_list = [
                str(row['course_difficulty']), 
                str(row['course_organization']),
                str(row['course_Certificate_type'])
            ]
            
            # Create the Program object
            program = Program(
                id=str(uuid.uuid4()),
                name=row['course_title'],         # Mapping course_title -> name
                description=syn_description,      # Mapping constructed description
                tags=json.dumps(tags_list),       # Storing tags as JSON string
                skills=json.dumps([])             # Empty list for now
            )
            programs_to_add.append(program)

        # Bulk insert for speed
        db.add_all(programs_to_add)
        
        # 4. Create a Dummy Student for testing
        test_student = Student(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="Test User",
            email="test@example.com",
            interests=json.dumps(["Python", "Machine Learning"]),
            grades=json.dumps({"math": 90})
        )
        db.add(test_student)
        
        db.commit()
        print(f"✅ Successfully initialized DB with {len(programs_to_add)} courses.")
        
    except FileNotFoundError:
        print("❌ ERROR: Could not find 'coursea_data.csv'. Make sure it is inside the 'backend' folder.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()