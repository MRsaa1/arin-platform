// TypeScript types for ARIN Platform

export interface Agent {
  agent_id: string
  agent_name: string
  status: 'initializing' | 'idle' | 'analyzing' | 'learning' | 'reporting' | 'error'
  metrics: {
    tasks_processed: number
    tasks_failed: number
    last_task_time: string | null
    average_processing_time: number
  }
}

export interface RiskAnalysis {
  task_id: string
  timestamp: string
  status: string
  results: {
    agent_results: Record<string, any>
    overall_status: string
  }
}

export interface GraphNode {
  id: string
  type: string
  label: string
  risk_score: number
  properties: Record<string, any>
}

export interface GraphEdge {
  source: string
  target: string
  type: string
  weight: number
  properties: Record<string, any>
}

export interface Alert {
  alert_id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  risk_type?: string
  message: string
  timestamp: string
}

