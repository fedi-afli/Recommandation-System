import { useState } from 'react'

interface Recommendation {
  program_id: string
  program_name: string
  score: number
  explanation: string
  tags: string[] | string 
  skills: string[] | string

}

interface RecommendationsListProps {
  recommendations: Recommendation[]
  onFeedback: (programId: string, feedbackType: 'clicked' | 'accepted') => void
}

function RecommendationsList({ recommendations, onFeedback }: RecommendationsListProps) {
  const [acceptedPrograms, setAcceptedPrograms] = useState<Set<string>>(new Set())

  const handleAccept = (programId: string) => {
    setAcceptedPrograms((prev) => new Set(prev).add(programId))
    onFeedback(programId, 'accepted')
  }

  const handleClick = (programId: string) => {
    onFeedback(programId, 'clicked')
  }

  // Helper to safely parse lists
  const parseList = (data: string[] | string | undefined) => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    try {
      return JSON.parse(data.replace(/'/g, '"'));
    } catch (e) {
      return [];
    }
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="card">
        <p style={{ textAlign: 'center', color: '#666' }}>
          No recommendations found. Try updating your profile.
        </p>
      </div>
    )
  }

  return (
    <div className="recommendations-grid">
      {recommendations.map((rec) => {
        const safeTags = parseList(rec.tags);
        const safeSkills = parseList(rec.skills);

        return (
          <div
            key={rec.program_id}
            className="recommendation-card"
            onClick={() => handleClick(rec.program_id)}
          >
            <div>
              <h3>
                {rec.program_name}
                <span className="score-badge">
                  {Math.round(rec.score * 100)}% Match
                </span>
              </h3>
            </div>

            <div className="explanation">{rec.explanation}</div>

            {/* DESCRIPTION SECTION REMOVED HERE */}

            {safeSkills.length > 0 && (
              <div>
                <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem', color: '#555' }}>
                  Skills you'll develop:
                </h4>
                <div className="tags">
                  {safeSkills.slice(0, 4).map((skill: string, index: number) => (
                    <span key={index} className="tag">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {safeTags.length > 0 && (
              <div>
                <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem', color: '#555' }}>
                  Related topics:
                </h4>
                <div className="tags">
                  {safeTags.slice(0, 6).map((tag: string, index: number) => (
                    <span key={index} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="feedback-section">
              <button
                className={`feedback-button ${
                  acceptedPrograms.has(rec.program_id) ? 'accepted' : ''
                }`}
                onClick={(e) => {
                  e.stopPropagation()
                  handleAccept(rec.program_id)
                }}
              >
                {acceptedPrograms.has(rec.program_id)
                  ? 'Accepted'
                  : "I'm Interested"}
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default RecommendationsList