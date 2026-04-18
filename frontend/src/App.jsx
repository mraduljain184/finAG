import { useState } from 'react'
import { Search, TrendingUp, Loader2, Download, AlertCircle } from 'lucide-react'
import { analyzeStock, downloadPDF } from './api/client'
import ReportView from './components/ReportView'
import AgentProgress from './components/AgentProgress'

function App() {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [downloading, setDownloading] = useState(false)

  const handleAnalyze = async () => {
    if (!ticker.trim()) return
    setLoading(true)
    setError(null)
    setReport(null)

    try {
      const data = await analyzeStock(ticker.trim())
      setReport(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze stock. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!report) return
    setDownloading(true)
    try {
      await downloadPDF(report.ticker)
    } catch (err) {
      setError('Failed to download PDF')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="text-primary-500" size={28} />
            <h1 className="text-2xl font-bold text-slate-900">finAG</h1>
            <span className="text-xs text-slate-500 ml-2">AI Equity Research</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Search Section */}
        {!report && (
          <div className="text-center py-20">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              AI-Powered Equity Research
            </h2>
            <p className="text-lg text-slate-600 mb-12 max-w-2xl mx-auto">
              Enter any stock ticker and get a complete research report in seconds.
              Powered by 5 specialized AI agents analyzing financials, news, technicals, and competitors.
            </p>

            <div className="max-w-md mx-auto">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                    onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                    placeholder="AAPL, MSFT, TSLA..."
                    className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled={loading}
                  />
                </div>
                <button
                  onClick={handleAnalyze}
                  disabled={loading || !ticker.trim()}
                  className="px-6 py-3 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? <Loader2 className="animate-spin" size={20} /> : 'Analyze'}
                </button>
              </div>

              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'].map((t) => (
                  <button
                    key={t}
                    onClick={() => { setTicker(t); }}
                    disabled={loading}
                    className="px-3 py-1 text-sm text-slate-600 bg-white border border-slate-200 rounded-full hover:bg-slate-100"
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {loading && <AgentProgress />}

            {error && (
              <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg max-w-lg mx-auto flex items-start gap-3">
                <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-sm text-red-700 text-left">{error}</p>
              </div>
            )}
          </div>
        )}

        {/* Report View */}
        {report && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={() => { setReport(null); setTicker(''); }}
                className="text-sm text-slate-600 hover:text-slate-900"
              >
                ← New analysis
              </button>
              <button
                onClick={handleDownloadPDF}
                disabled={downloading}
                className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50"
              >
                {downloading ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
                Download PDF
              </button>
            </div>
            <ReportView report={report} />
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 mt-12 py-6">
        <div className="max-w-6xl mx-auto px-6 text-center text-sm text-slate-500">
          finAG — Built with CrewAI, FastAPI, and React
        </div>
      </footer>
    </div>
  )
}

export default App