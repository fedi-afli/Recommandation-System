from typing import List, Dict, Any
from .recommender import content_recommender  # Import the file you just updated
from .matrix_factorization import als_recommender # Import your matrix engine

class HybridRecommender:
    """
    Combines Content-Based (Text/Filters) + Collaborative Filtering (User Behavior).
    """
    
    def recommend(self, student_data: Dict[str, Any], programs: List[Dict], top_k: int = 5):
        """
        Main function called by your API.
        """
        # 1. Ensure models are trained
        if content_recommender.programs_df is None:
            print("🔄 Training Content Model on the fly...")
            content_recommender.fit(programs)
            
        if not als_recommender.fitted:
            print("🔄 Training Matrix Model on the fly...")
            als_recommender.fit()

        # 2. Get Content Recommendations (This applies the Hard Filters: GPA/Field)
        # content_recs is a list of Dicts with 'match_score'
        content_recs = content_recommender.recommend(student_data, top_k=20)
        
        # Convert to a dictionary for easy lookup: {program_id: score}
        combined_scores = {}
        program_lookup = {str(p['id']): p for p in programs}

        # Weighting Strategy
        # If we have little user data, trust Content (0.8) more than Matrix (0.2)
        w_content = 0.7
        w_matrix = 0.3

        # 3. Process Content Scores
        for item in content_recs:
            pid = str(item['id'])
            # Normalize score (usually 0-1 already)
            combined_scores[pid] = item['match_score'] * w_content

        # 4. Process Matrix Scores (Boost popular items)
        student_id = str(student_data.get('id', ''))
        
        # Only boost items that passed the Content Filter (i.e., are in combined_scores)
        # This ensures we don't recommend "Physics" to an "Arts" student just because it's popular.
        for pid in combined_scores.keys():
            matrix_score = als_recommender.predict(student_id, pid)
            if matrix_score > 0:
                combined_scores[pid] += (matrix_score * w_matrix)

        # 5. Sort Final Results
        sorted_ids = sorted(combined_scores, key=combined_scores.get, reverse=True)[:top_k]
        
        final_results = []
        for pid in sorted_ids:
            if pid in program_lookup:
                prog = program_lookup[pid]
                prog['final_score'] = combined_scores[pid]
                # Add a simple explanation string
                prog['explanation'] = "Matches your field & interests"
                final_results.append(prog)

        return final_results

# Create the global instance
hybrid_recommender = HybridRecommender()