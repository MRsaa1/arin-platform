'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

export default function GraphVisualization() {
  const [graphData, setGraphData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchGraph()
  }, [])

  const fetchGraph = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/graph`
      )
      setGraphData(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch graph:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-saa-white">Loading graph...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-saa-white mb-8">Dependency Graph</h1>
      
      <div className="saa-card">
        <div className="mb-4">
          <div className="text-saa-white/70 mb-2">
            Nodes: <span className="text-saa-gold font-semibold">{graphData?.statistics?.nodes_count || 0}</span>
          </div>
          <div className="text-saa-white/70">
            Edges: <span className="text-saa-gold font-semibold">{graphData?.statistics?.edges_count || 0}</span>
          </div>
        </div>
        
        <div className="text-saa-white/50 text-sm">
          Graph visualization will be implemented with D3.js or similar library
        </div>
      </div>
    </div>
  )
}

