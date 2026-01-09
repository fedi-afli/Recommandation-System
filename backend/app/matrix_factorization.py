import numpy as np
import scipy.sparse as sp
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Feedback, Recommendation

class ALSMatrixFactorization:
    """
    Alternating Least Squares (ALS) matrix factorization for collaborative filtering.
    Adapted for Local SQLite Database.
    """

    def __init__(self, n_factors: int = 20, n_iterations: int = 10, reg_lambda: float = 0.1):
        self.n_factors = n_factors
        self.n_iterations = n_iterations
        self.reg_lambda = reg_lambda

        self.user_index: Dict[str, int] = {}
        self.item_index: Dict[str, int] = {}
        self.user_factors: np.ndarray = None
        self.item_factors: np.ndarray = None

        self.fitted = False
        self.n_users = 0
        self.n_items = 0

    def _gather_interactions(self) -> Dict[Tuple[str, str], float]:
        """
        Gather user-item interactions from SQLite.
        """
        interactions = {}
        db: Session = SessionLocal()
        
        try:
            # 1. Get explicit feedback (clicks/ratings)
            feedbacks = db.query(Feedback).all()
            for f in feedbacks:
                weight = 0.0
                if f.clicked: weight += 1.0
                if f.accepted: weight += 3.0
                if f.rating: weight += (f.rating / 5.0) * 2.0
                
                if weight > 0:
                    interactions[(f.student_id, f.program_id)] = interactions.get((f.student_id, f.program_id), 0.0) + weight

            # 2. Get implicit feedback (previous recommendations shown)
            # giving a small weight just for being shown allows discovery
            recs = db.query(Recommendation).all()
            for r in recs:
                if r.program_id:
                    current = interactions.get((r.student_id, r.program_id), 0.0)
                    if current == 0:
                        interactions[(r.student_id, r.program_id)] = 0.1

        except Exception as e:
            print(f"Error gathering interactions: {e}")
        finally:
            db.close()

        return interactions

    def _build_interaction_matrix(self, interactions: Dict[Tuple[str, str], float]) -> sp.csr_matrix:
        users = sorted({u for (u, _) in interactions.keys()})
        items = sorted({i for (_, i) in interactions.keys()})

        self.user_index = {u: idx for idx, u in enumerate(users)}
        self.item_index = {i: idx for idx, i in enumerate(items)}

        self.n_users = len(users)
        self.n_items = len(items)

        rows = []
        cols = []
        data = []

        for (u, i), w in interactions.items():
            rows.append(self.user_index[u])
            cols.append(self.item_index[i])
            data.append(w)

        return sp.csr_matrix((data, (rows, cols)), shape=(self.n_users, self.n_items))

    def _als_step(self, ratings: sp.csr_matrix, solve_vecs: np.ndarray, fixed_vecs: np.ndarray) -> np.ndarray:
        # Standard ALS implementation
        new_vecs = np.zeros_like(solve_vecs)
        for i in range(solve_vecs.shape[0]):
            if ratings.indptr[i] != ratings.indptr[i + 1]:
                row_data = ratings.data[ratings.indptr[i]:ratings.indptr[i + 1]]
                row_indices = ratings.indices[ratings.indptr[i]:ratings.indptr[i + 1]]
                
                # Simple implementation without confidence matrix for stability in small data
                Y_u = fixed_vecs[row_indices]
                A_u = Y_u.T.dot(np.diag(row_data)).dot(Y_u) + self.reg_lambda * np.eye(self.n_factors)
                b_u = Y_u.T.dot(np.diag(row_data)).dot(np.ones(len(row_data))) # Target is 1 for interaction
                
                try:
                    new_vecs[i] = np.linalg.solve(A_u, b_u)
                except np.linalg.LinAlgError:
                    new_vecs[i] = solve_vecs[i] # Fallback
            else:
                new_vecs[i] = solve_vecs[i]
        return new_vecs

    def fit(self) -> bool:
        interactions = self._gather_interactions()
        if len(interactions) < 2:
            print("⚠️ Not enough data to train Matrix Factorization.")
            self.fitted = False
            return False

        ratings = self._build_interaction_matrix(interactions)
        
        # Initialize factors
        self.user_factors = np.random.normal(0, 0.1, (self.n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (self.n_items, self.n_factors))

        # Optimization loop
        for _ in range(self.n_iterations):
            self.user_factors = self._als_step(ratings, self.user_factors, self.item_factors)
            self.item_factors = self._als_step(ratings.T.tocsr(), self.item_factors, self.user_factors)

        self.fitted = True
        print(f"✅ ALS Model trained on {len(interactions)} interactions.")
        return True

    def predict(self, user_id: str, item_id: str) -> float:
        if not self.fitted: return 0.0
        u_idx = self.user_index.get(user_id)
        i_idx = self.item_index.get(item_id)
        
        if u_idx is None or i_idx is None:
            return 0.0
            
        return float(np.dot(self.user_factors[u_idx], self.item_factors[i_idx]))

# Global Instance
als_recommender = ALSMatrixFactorization()