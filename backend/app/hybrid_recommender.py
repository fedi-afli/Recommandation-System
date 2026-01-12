from typing import List, Dict, Any
from .recommender import content_recommender  
from .matrix_factorization import als_recommender 

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

    
        content_recs = content_recommender.recommend(student_data, top_k=20)
   
        combined_scores = {}
        program_lookup = {str(p['id']): p for p in programs}


        w_content = 0.7
        w_matrix = 0.3

   
        for item in content_recs:
            pid = str(item['id'])
         
            combined_scores[pid] = item['match_score'] * w_content

      
        student_id = str(student_data.get('id', ''))
        

        for pid in combined_scores.keys():
            matrix_score = als_recommender.predict(student_id, pid)
            if matrix_score > 0:
                combined_scores[pid] += (matrix_score * w_matrix)

        sorted_ids = sorted(combined_scores, key=combined_scores.get, reverse=True)[:top_k]
        
        final_results = []
        for pid in sorted_ids:
            if pid in program_lookup:
                prog = program_lookup[pid]
                prog['final_score'] = combined_scores[pid]
        
                prog['explanation'] = "Matches your field & interests"
                final_results.append(prog)

        return final_results

hybrid_recommender = HybridRecommender()