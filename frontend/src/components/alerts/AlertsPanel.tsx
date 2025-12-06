'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

interface Alert {
  alert_id: string
  severity: string
  risk_type?: string
  message: string
  timestamp: string
}

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/alerts`
      )
      setAlerts(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500 bg-red-500/10'
      case 'high':
        return 'border-orange-500 bg-orange-500/10'
      case 'medium':
        return 'border-yellow-500 bg-yellow-500/10'
      default:
        return 'border-saa-border bg-saa-gray'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-saa-white">Loading alerts...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-saa-white mb-8">Alerts</h1>
      
      <div className="space-y-4">
        {alerts.map((alert) => (
          <div
            key={alert.alert_id}
            className={`saa-card border-l-4 ${getSeverityColor(alert.severity)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold capitalize ${
                    alert.severity === 'critical' ? 'bg-red-500 text-white' :
                    alert.severity === 'high' ? 'bg-orange-500 text-white' :
                    alert.severity === 'medium' ? 'bg-yellow-500 text-black' :
                    'bg-saa-gray text-saa-white'
                  }`}>
                    {alert.severity}
                  </span>
                  {alert.risk_type && (
                    <span className="text-sm text-saa-white/70">{alert.risk_type}</span>
                  )}
                </div>
                <p className="text-saa-white mb-2">{alert.message}</p>
                <div className="text-xs text-saa-white/50">
                  {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {alerts.length === 0 && (
        <div className="text-center py-12">
          <div className="text-saa-white/50">No alerts</div>
        </div>
      )}
    </div>
  )
}

