'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

interface Agent {
  agent_id: string
  agent_name: string
  status: string
  metrics: {
    tasks_processed: number
    tasks_failed: number
    average_processing_time: number
  }
}

export default function AgentsDashboard() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAgents()
    const interval = setInterval(fetchAgents, 5000) // Обновление каждые 5 секунд
    return () => clearInterval(interval)
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/agents`)
      setAgents(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch agents:', error)
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'bg-green-500'
      case 'analyzing':
        return 'bg-saa-gold'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-saa-white">Loading agents...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-saa-white mb-8">Agents Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.agent_id} className="saa-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-saa-white">{agent.agent_name}</h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`}></div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-saa-white/70">Status:</span>
                <span className="text-saa-white font-medium capitalize">{agent.status}</span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-saa-white/70">Tasks Processed:</span>
                <span className="text-saa-gold font-semibold">{agent.metrics.tasks_processed}</span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-saa-white/70">Tasks Failed:</span>
                <span className="text-red-400 font-semibold">{agent.metrics.tasks_failed}</span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-saa-white/70">Avg Time:</span>
                <span className="text-saa-white font-medium">
                  {agent.metrics.average_processing_time.toFixed(2)}s
                </span>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-saa-border">
              <div className="text-xs text-saa-white/50">ID: {agent.agent_id}</div>
            </div>
          </div>
        ))}
      </div>
      
      {agents.length === 0 && (
        <div className="text-center py-12">
          <div className="text-saa-white/50">No agents available</div>
        </div>
      )}
    </div>
  )
}

