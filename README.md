Study Program Recommender System
A high-performance, Context-Aware Hybrid Recommendation System designed to help students discover Coursera study programs. It combines strict "Smart Filters" (Field of Study, GPA) with AI-powered Content-Based Filtering to suggest the best matches instantly.

Features
 Instant Recommendations: "One-Step" architecture provides results in milliseconds using in-memory data.

 Context-Aware AI: Uses TF-IDF Vectorization and Cosine Similarity to match student interests with course descriptions and tags.

 Smart Filters: Automatically applies "Hard Constraints" to filter out courses that don't match the student's Field of Study or GPA requirements before the AI ranks the rest.

 Auto-Cleaning Data Pipeline: Robust backend that automatically cleans, normalizes, and fixes CSV data on startup.

 In-Memory Performance: Loads the dataset into Pandas for lightning-fast retrieval without database latency.

 Full Docker Support: Unified container orchestration for Backend, Frontend, and an Evaluation environment (Jupyter Lab).

📊 Integrated Evaluation: Dedicated Jupyter environment for testing metrics like Precision@K and NDCG@K directly against the backend logic.

Architecture
Backend (FastAPI + Python)
Data Source: coursea_data.csv (In-memory Pandas DataFrame).

Smart Filters: Validates Hard Constraints (GPA, Field).

AI Engine: scikit-learn TF-IDF Vectorizer.

API: Unified /recommend endpoint.

Frontend (React + TypeScript)
Framework: Vite + React 18.

Routing: React Router v6.

State: Local state management for fast interactions.

Evaluation (Jupyter Lab)
Environment: Pre-configured Data Science container.

Access: Direct access to backend code and data for seamless model testing.

Prerequisites
Docker and Docker Compose (Recommended)

Python 3.9+ (For local development)

Node.js 18+ (For local development)

Quick Start (Docker)
This is the easiest way to run the entire suite (Frontend, Backend, and Evaluation).

1. Build and Run
Bash

docker-compose up --build
2. Access Services
Frontend App: http://localhost:80

Backend API Docs: http://localhost:8000/docs

Evaluation (Jupyter): http://localhost:8888

Password: easytoken

Quick Start (Local Development)
Backend
Navigate to the backend:

Bash

cd backend
Create and activate virtual environment:

Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

Bash

pip install -r requirements.txt
Run the server:

Bash

uvicorn main:app --reload
Frontend
Navigate to the frontend:

Bash

cd frontend
Install dependencies:

Bash

npm install
Run the development server:

Bash

npm run dev
API Endpoints
Core Endpoint
POST /recommend

This single endpoint handles the entire logic. It accepts student data, cleans it, filters the dataset, and runs the AI model.

Request Body:

JSON

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "field": "Data Science",
  "gpa": 85.5,
  "interests": ["Python", "Machine Learning", "Statistics"],
  "grades": {}
}
Utility
GET / Health check that returns the number of courses currently loaded in memory.

How It Works (The "Smart Hybrid" Logic)
Data Ingestion: On startup, main.py loads coursea_data.csv. It renames columns (e.g., "Skills" -> "tags"), fills missing data, and trains the TF-IDF model on course descriptions + tags.

User Input: The user fills out the form on the React frontend.

Smart Filtering (Hard Constraints):

GPA Check: Removes courses where Course Min GPA > Student GPA.

Field Check: Removes courses where Course Field != Student Field (unless the course is "General").

Content Matching (Soft Constraints):

The remaining courses are compared against the student's interests using Cosine Similarity.

Ranking & Explanation: The top 5 courses with the highest similarity scores are returned, along with an explanation of why they matched (e.g., "Matches your interest in 'Python'").

Project Structure
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── hybrid_recommender.py   # Orchestrates Filters + AI
│   │   ├── recommender.py          # TF-IDF Logic
│   │   ├── models.py               # Pydantic Schemas
│   │   └── ...
│   ├── main.py                     # Entry point & Data Cleaning
│   ├── coursea_data.csv            # The Dataset
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StudentForm.tsx     # Input UI
│   │   │   └── RecommendationsList.tsx # Results UI
│   │   ├── App.tsx
│   │   └── ...
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── evaluation/
│   └── recommendation_evaluation.ipynb # Offline metrics (Precision@K, NDCG)
├── docker-compose.yml
└── README.md
Troubleshooting
"Internal Server Error" / 500

Check your terminal logs.

Ensure coursea_data.csv is present in the backend/ folder.

Ensure the CSV has headers. The system tries to auto-detect them, but course_title or Course Name are required.

"Failed to fetch" (Frontend)

Ensure the Backend is running on port 8000.

If using Docker, ensure ports are not blocked by another service.

License
MIT License.

Contributors
Built as a demonstration of a robust, CSV-powered recommendation architecture.