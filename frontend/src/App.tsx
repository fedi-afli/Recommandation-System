import { useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import StudentForm from './components/StudentForm'
import RecommendationsList from './components/RecommendationsList'
import './index.css'

// Interfaces
interface Student {
  name: string
  email: string
  field: string
  gpa: number
  interests: string[]
  grades: Record<string, number>
}

interface Recommendation {
  program_id: string
  program_name: string
  program_description: string
  score: number
  explanation: string
  tags: string[] | string
  skills: string[] | string
}

const API_BASE = 'http://localhost:8000'

function App() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const navigate = useNavigate()

  // --- THE FIXED FUNCTION ---
  const handleStudentSubmit = async (studentData: Student) => {
    setLoading(true)
    setError(null)
    setRecommendations([]) // Clear old results

    try {
      console.log("Sending data:", studentData);

      // 1. ONE STEP ONLY: Send data -> Get Recommendations
      const response = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentData),
      })

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`)
      }

      const data = await response.json()
      console.log("Received data:", data);

      // 2. Map Backend Data to Frontend Format
      // The backend returns raw CSV fields + 'final_score'
      // We convert them to what RecommendationsList expects
      const formattedRecs = data.map((item: any) => ({
        program_id: item.id || item.Course_Name, // Fallback if ID is missing
        program_name: item.Course_Name || item.name,
        program_description: item.Description || item.description,
        score: item.final_score || 0,
        explanation: item.explanation || "Matches your profile",
        tags: item.Tags || [],
        skills: item.Skills || []
      }))

      setRecommendations(formattedRecs)

      // 3. Navigate to results
      navigate('/recommendations')

    } catch (err) {
      console.error(err)
      setError('Failed to get recommendations. Ensure Backend is running.')
    } finally {
      setLoading(false)
    }
  }

  // (Optional) Feedback Placeholder - You can enable this later if you add the DB back
  const handleFeedback = (programId: string, type: string) => {
    console.log(`User ${type} on program ${programId}`);
    alert("Feedback noted! (This feature is simplified for now)");
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🎓 Study Program Recommender</h1>
        <p>Discover programs that match your <strong>Field</strong>, <strong>GPA</strong>, and <strong>Interests</strong>.</p>
      </div>

      {error && (
        <div className="error">{error}</div>
      )}

      <Routes>
        {/* Page 1: Input Form */}
        <Route 
          path="/" 
          element={
            <StudentForm onSubmit={handleStudentSubmit} loading={loading} />
          } 
        />

        {/* Page 2: Recommendations List */}
        <Route 
          path="/recommendations" 
          element={
            <>
              <button 
                onClick={() => navigate('/')}
                style={{ marginBottom: '1rem', cursor: 'pointer', background: 'none', border: 'none', color: '#667eea', fontWeight: 'bold' }}
              >
                ← Start Over
              </button>
              
              <RecommendationsList
                recommendations={recommendations}
                onFeedback={handleFeedback}
              />
            </>
          } 
        />
      </Routes>
    </div>
  )
}

export default App