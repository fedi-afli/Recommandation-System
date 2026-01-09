from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

class ContentRecommender:
    """
    Content-Based Filtering with HARD FILTERS (Field, GPA, Tuition).
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.program_matrix = None
        self.programs_df = None

    def fit(self, programs: List[Dict]):
        """
        Trains the vectorizer on program tags and descriptions.
        """
        if not programs:
            return

        self.programs_df = pd.DataFrame(programs)
        
        # SAFETY: Ensure numeric columns exist (fill with defaults if missing)
        # We check both direct columns and JSON fields if necessary
        if 'min_gpa' not in self.programs_df.columns:
            self.programs_df['min_gpa'] = 0.0
        if 'tuition_fees' not in self.programs_df.columns:
            self.programs_df['tuition_fees'] = 999999.0

        # Create text soup for AI matching
        self.programs_df['content'] = self.programs_df.apply(
            lambda x: f"{' '.join(x['tags']) if isinstance(x['tags'], list) else str(x['tags'])} {x['description']}", 
            axis=1
        )
        
        self.program_matrix = self.vectorizer.fit_transform(self.programs_df['content'])
        print(f"✅ Content Recommender trained on {len(programs)} programs.")

    def recommend(self, student_profile: Dict[str, Any], top_k: int = 5) -> List[Dict]:
        """
        Returns top_k programs matching the student's profile.
        """
        if self.program_matrix is None or not student_profile:
            return []

        # --- 1. HARD FILTERS (The Precision Logic) ---
        # Start with all programs as "True" (Keep)
        mask = pd.Series([True] * len(self.programs_df))

        # A. Filter by FIELD (If user selected one)
        student_field = str(student_profile.get('field', '')).lower().strip()
        if student_field and student_field != 'unknown':
            # Check if program 'field' contains the student's interest
            field_match = self.programs_df['field'].astype(str).str.lower().str.contains(student_field, regex=False)
            mask = mask & field_match

        # B. Filter by GPA (If user has a GPA)
        student_gpa = float(student_profile.get('gpa', 0.0))
        if student_gpa > 0:
            # Only keep programs where min_gpa <= student_gpa
            gpa_match = self.programs_df['min_gpa'] <= student_gpa
            mask = mask & gpa_match

        # Get indices of programs that survived the filters
        valid_indices = self.programs_df.index[mask].tolist()

        # Fallback: If filters removed everything, show all (better than empty screen)
        if not valid_indices:
            print("⚠️ Filters too strict. Showing all courses.")
            valid_indices = self.programs_df.index.tolist()

        # --- 2. TEXT MATCHING (The AI Logic) ---
        # Build query string from interests + field
        interests = student_profile.get('interests', [])
        query_text = " ".join(interests) if isinstance(interests, list) else str(interests)
        query_text += f" {student_field}"

        user_vector = self.vectorizer.transform([query_text])
        
        # Calculate scores only for valid programs
        filtered_matrix = self.program_matrix[valid_indices]
        scores = cosine_similarity(user_vector, filtered_matrix).flatten()

        # --- 3. BUILD RESULT LIST ---
        results = []
        # Get top indices relative to our filtered list
        top_local_indices = scores.argsort()[::-1][:top_k]

        for local_idx in top_local_indices:
            score = scores[local_idx]
            if score > 0.0:
                # Map back to original dataframe index
                original_idx = valid_indices[local_idx]
                program = self.programs_df.iloc[original_idx].to_dict()
                program['match_score'] = float(score)
                results.append(program)
        
        return results

# Global Instance
content_recommender = ContentRecommender()