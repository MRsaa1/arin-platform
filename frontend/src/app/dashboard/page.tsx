'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/common/Header'
import AgentsDashboard from '@/components/agents/AgentsDashboard'
import RisksDashboard from '@/components/risks/RisksDashboard'
import GraphVisualization from '@/components/graph/GraphVisualization'
import AlertsPanel from '@/components/alerts/AlertsPanel'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'agents' | 'risks' | 'graph' | 'alerts'>('agents')
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    // Триггер анимации при загрузке страницы
    setIsLoaded(true)
  }, [])

  return (
    <div className="min-h-screen bg-saa-dark">
      <Header />
      
      <main className="container mx-auto px-4 py-12">
        {/* Hero Section - в стиле SAA Alliance */}
        <div className="text-center mb-16">
          {/* Верхняя анимированная золотая линия - появляется при загрузке */}
          {isLoaded && (
            <div className="saa-gold-line-continuous mb-6"></div>
          )}
          
          <h1 className="text-5xl md:text-6xl font-bold text-saa-white mb-4 tracking-tight">
            AUTONOMOUS RISK
            <br />
            INTELLIGENCE NETWORK
          </h1>
          <p className="text-xl text-saa-white/80 mb-6">
            Premium Research & Wealth Intelligence
          </p>
          
          {/* Нижняя анимированная золотая линия - появляется при загрузке */}
          {isLoaded && (
            <div className="saa-gold-line-continuous mt-6"></div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-4 mb-8 border-b border-saa-border">
          <button
            onClick={() => setActiveTab('agents')}
            className={`px-6 py-3 font-semibold transition-colors text-sm ${
              activeTab === 'agents'
                ? 'text-saa-gold border-b-2 border-saa-gold'
                : 'text-saa-white hover:text-saa-gold'
            }`}
          >
            Agents
          </button>
          <button
            onClick={() => setActiveTab('risks')}
            className={`px-6 py-3 font-semibold transition-colors text-sm ${
              activeTab === 'risks'
                ? 'text-saa-gold border-b-2 border-saa-gold'
                : 'text-saa-white hover:text-saa-gold'
            }`}
          >
            Risks
          </button>
          <button
            onClick={() => setActiveTab('graph')}
            className={`px-6 py-3 font-semibold transition-colors text-sm ${
              activeTab === 'graph'
                ? 'text-saa-gold border-b-2 border-saa-gold'
                : 'text-saa-white hover:text-saa-gold'
            }`}
          >
            Graph
          </button>
          <button
            onClick={() => setActiveTab('alerts')}
            className={`px-6 py-3 font-semibold transition-colors text-sm ${
              activeTab === 'alerts'
                ? 'text-saa-gold border-b-2 border-saa-gold'
                : 'text-saa-white hover:text-saa-gold'
            }`}
          >
            Alerts
          </button>
        </div>

        {/* Content */}
        <div className="mt-8">
          {activeTab === 'agents' && <AgentsDashboard />}
          {activeTab === 'risks' && <RisksDashboard />}
          {activeTab === 'graph' && <GraphVisualization />}
          {activeTab === 'alerts' && <AlertsPanel />}
        </div>
      </main>

      {/* Footer - в стиле SAA Alliance */}
      <footer className="border-t border-saa-border mt-16 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-saa-white/60">
          © 2025 Scientific Analytics Alliance • Premium Research & Wealth Intelligence
        </div>
      </footer>
    </div>
  )
}

