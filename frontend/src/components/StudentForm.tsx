import { useState } from 'react'

interface StudentFormProps {
  onSubmit: (data: {
    name: string
    email: string
    field: string        // <--- NEW: Required for filtering
    gpa: number          // <--- NEW: Calculated from grades
    interests: string[]
    grades: Record<string, number>
  }) => void
  loading: boolean
}

// Fields must match your CSV data categories roughly
const studyFields = [
  'Business',
  'Technology & CS',
  'Health & Medicine',
  'Arts & Humanities',
  'Science & Engineering',
  'Social Sciences',
  'Data Science',
  'Personal Development'
]

const availableInterests = [
  'art', 'biology', 'business', 'chemistry', 'computers', 'design',
  'drawing', 'engineering', 'environment', 'fashion', 'health', 'history',
  'math', 'music', 'nature', 'people', 'physics', 'programming',
  'psychology', 'science', 'technology', 'writing',
]

const subjects = [
  'math', 'physics', 'chemistry', 'biology', 'english',
  'history', 'geography', 'art', 'music', 'computer science',
]

function StudentForm({ onSubmit, loading }: StudentFormProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [field, setField] = useState('') // <--- NEW STATE
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [grades, setGrades] = useState<Record<string, number>>({})

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : [...prev, interest]
    )
  }

  const handleGradeChange = (subject: string, value: string) => {
    const numValue = parseFloat(value)
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 100) {
      setGrades((prev) => ({ ...prev, [subject]: numValue }))
    } else if (value === '') {
      setGrades((prev) => {
        const newGrades = { ...prev }
        delete newGrades[subject]
        return newGrades
      })
    }
  }

  // Helper to calculate Average Grade (GPA)
  const calculateAverage = () => {
    const values = Object.values(grades)
    if (values.length === 0) return 0
    const sum = values.reduce((a, b) => a + b, 0)
    return (sum / values.length)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // 1. Validation: Ensure Field is selected
    if (!name || !email || !field || selectedInterests.length === 0) {
      alert('Please fill in name, email, field, and at least one interest.')
      return
    }

    // 2. Calculate GPA (Average of entered grades)
    // If no grades entered, default to 0 (or a neutral score like 70)
    const calculatedGPA = calculateAverage()

    // 3. Send Data to Parent
    // This matches the structure your new Backend expects!
    onSubmit({
      name,
      email,
      field,       // Backend uses this for "Hard Filter"
      gpa: calculatedGPA, // Backend uses this for "Eligibility Check"
      interests: selectedInterests,
      grades,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 style={{ marginBottom: '1.5rem' }}>Tell us about yourself</h2>

      <div className="form-group">
        <label htmlFor="name">Name *</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
        />
      </div>

      {/* --- NEW FIELD DROPDOWN --- */}
      <div className="form-group">
        <label htmlFor="field">Field of Interest *</label>
        <select
          id="field"
          value={field}
          onChange={(e) => setField(e.target.value)}
          required
          style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
        >
          <option value="">Select your main field...</option>
          {studyFields.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <small style={{ color: '#666' }}>
          We use this to filter out courses that don't match your goals.
        </small>
      </div>

      <div className="form-group">
        <label>Interests * (select at least one)</label>
        <div className="interests-grid">
          {availableInterests.map((interest) => (
            <button
              key={interest}
              type="button"
              className={`interest-tag ${
                selectedInterests.includes(interest) ? 'selected' : ''
              }`}
              onClick={() => toggleInterest(interest)}
            >
              {interest}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Your Grades (0-100, optional)</label>
        <p style={{fontSize: '0.85rem', color: '#666', marginBottom: '0.5rem'}}>
          We average these to check if you meet course GPA requirements.
        </p>
        <div className="grades-grid">
          {subjects.map((subject) => (
            <div key={subject} className="grade-input">
              <label htmlFor={subject}>{subject}</label>
              <input
                id={subject}
                type="number"
                min="0"
                max="100"
                value={grades[subject] || ''}
                onChange={(e) => handleGradeChange(subject, e.target.value)}
                placeholder="-"
              />
            </div>
          ))}
        </div>
      </div>

      <button 
        type="submit" 
        className="button" 
        disabled={loading}
        style={{ marginTop: '1rem' }}
      >
        {loading ? 'Analyzing Profile...' : 'Get Recommendations'}
      </button>
    </form>
  )
}

export default StudentForm