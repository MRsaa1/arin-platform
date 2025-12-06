'use client'

import { useState } from 'react'
import axios from 'axios'

export default function RisksDashboard() {
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/risks/analyze`,
        {
          type: 'comprehensive_analysis',
          entity_id: 'test_entity',
          entity_type: 'portfolio'
        }
      )
      setResult(response.data)
    } catch (error) {
      console.error('Failed to analyze risk:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-saa-white">Risk Analysis</h1>
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="saa-button"
        >
          {analyzing ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {result && (
        <div className="saa-card">
          <h2 className="text-xl font-semibold text-saa-white mb-4">Analysis Results</h2>
          <pre className="text-sm text-saa-white/80 overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

