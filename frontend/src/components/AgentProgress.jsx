import { useEffect, useState } from 'react'
import { CheckCircle2, Loader2, Circle } from 'lucide-react'

const AGENTS = [
  { id: 'financial', label: 'Financial Data Agent', desc: 'Fetching fundamentals from Yahoo Finance', duration: 4000 },
  { id: 'news', label: 'News Sentiment Agent', desc: 'Analyzing recent articles with AI', duration: 8000 },
  { id: 'technical', label: 'Technical Analysis Agent', desc: 'Computing RSI, MACD, moving averages', duration: 5000 },
  { id: 'competitor', label: 'Competitor Analysis Agent', desc: 'Identifying and comparing peers', duration: 12000 },
  { id: 'report', label: 'Report Writer Agent', desc: 'Synthesizing final recommendation', duration: 6000 },
]

function AgentProgress() {
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    let cumulativeDelay = 0
    const timers = []

    AGENTS.forEach((agent, i) => {
      cumulativeDelay += agent.duration
      const timer = setTimeout(() => {
        setActiveIndex(i + 1)
      }, cumulativeDelay)
      timers.push(timer)
    })

    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div className="mt-12 p-6 bg-white rounded-lg border border-slate-200 max-w-xl mx-auto text-left">
      <h3 className="text-center font-semibold text-slate-900 mb-1">
        Multi-Agent Pipeline Running
      </h3>
      <p className="text-center text-sm text-slate-500 mb-6">
        5 specialist agents are analyzing this stock
      </p>

      <div className="space-y-3">
        {AGENTS.map((agent, i) => {
          const isComplete = i < activeIndex
          const isActive = i === activeIndex
          const isPending = i > activeIndex

          return (
            <div
              key={agent.id}
              className={`flex items-start gap-3 p-3 rounded-lg transition-all ${
                isActive ? 'bg-primary-50 border border-primary-200' : ''
              }`}
            >
              <div className="mt-0.5 flex-shrink-0">
                {isComplete && <CheckCircle2 className="text-green-500" size={20} />}
                {isActive && <Loader2 className="text-primary-500 animate-spin" size={20} />}
                {isPending && <Circle className="text-slate-300" size={20} />}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`font-medium text-sm ${
                  isComplete ? 'text-slate-400 line-through' :
                  isActive ? 'text-primary-700' : 'text-slate-500'
                }`}>
                  {agent.label}
                </p>
                <p className={`text-xs ${
                  isActive ? 'text-primary-600' : 'text-slate-400'
                }`}>
                  {agent.desc}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      <p className="text-xs text-center text-slate-400 mt-6">
        Average analysis time: 30–60 seconds
      </p>
    </div>
  )
}

export default AgentProgress