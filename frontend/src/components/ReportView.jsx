import {
  TrendingUp,
  TrendingDown,
  Minus,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import PriceChart from "./PriceChart";

const recColors = {
  "Strong Buy": "bg-green-100 border-green-500 text-green-900",
  Buy: "bg-green-50 border-green-400 text-green-800",
  Hold: "bg-amber-50 border-amber-400 text-amber-800",
  Sell: "bg-red-50 border-red-400 text-red-800",
  "Strong Sell": "bg-red-100 border-red-500 text-red-900",
};

const sentimentColors = {
  Positive: "border-green-400 bg-green-50",
  Negative: "border-red-400 bg-red-50",
  Neutral: "border-slate-300 bg-slate-50",
};

function formatNum(n) {
  if (n === null || n === undefined) return "N/A";
  if (Math.abs(n) >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (Math.abs(n) >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n?.toLocaleString()}`;
}

function formatPct(v) {
  if (v === null || v === undefined) return "N/A";
  return `${(v * 100).toFixed(2)}%`;
}

function ReportView({ report }) {
  const r = report.report;
  const financial = report.financial.data;
  const technical = report.technical.data;
  const competitor = report.competitor;
  const news = report.news_sentiment;

  const upside =
    financial.current_price && r.target_price
      ? (
          ((r.target_price - financial.current_price) /
            financial.current_price) *
          100
        ).toFixed(1)
      : null;

  const recClass = recColors[r.recommendation] || recColors["Hold"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              {report.company_name}{" "}
              <span className="text-slate-500 font-normal">
                ({report.ticker})
              </span>
            </h1>
            <p className="text-slate-500 mt-1">
              {financial.sector} — {financial.industry}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-500">Current Price</p>
            <p className="text-3xl font-bold text-slate-900">
              ${financial.current_price?.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Recommendation Box */}
        <div className={`mt-6 p-6 border-l-4 rounded ${recClass}`}>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-sm uppercase tracking-wide opacity-75">
                Recommendation
              </p>
              <p className="text-4xl font-bold mt-1">{r.recommendation}</p>
            </div>
            <div className="grid grid-cols-3 gap-6 text-right">
              <div>
                <p className="text-xs uppercase opacity-75">Target</p>
                <p className="text-xl font-semibold">
                  ${r.target_price?.toFixed(2) || "N/A"}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase opacity-75">Upside</p>
                <p
                  className={`text-xl font-semibold ${upside >= 0 ? "text-green-700" : "text-red-700"}`}
                >
                  {upside !== null
                    ? `${upside > 0 ? "+" : ""}${upside}%`
                    : "N/A"}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase opacity-75">Confidence</p>
                <p className="text-xl font-semibold">
                  {r.confidence?.toFixed(0)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="mt-6">
          <h3 className="text-sm uppercase tracking-wide text-slate-500 mb-2">
            Executive Summary
          </h3>
          <p className="text-slate-700 leading-relaxed">
            {r.executive_summary}
          </p>
        </div>

        {/* Strengths & Risks */}
        <div className="mt-6 grid md:grid-cols-2 gap-4">
          <div className="p-4 bg-green-50 border-l-4 border-green-400 rounded">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="text-green-600" size={18} />
              <h3 className="font-semibold text-green-900">Key Strengths</h3>
            </div>
            <ul className="space-y-1 text-sm text-green-900">
              {r.key_strengths?.map((s, i) => (
                <li key={i}>• {s}</li>
              ))}
            </ul>
          </div>
          <div className="p-4 bg-red-50 border-l-4 border-red-400 rounded">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="text-red-600" size={18} />
              <h3 className="font-semibold text-red-900">Key Risks</h3>
            </div>
            <ul className="space-y-1 text-sm text-red-900">
              {r.key_risks?.map((risk, i) => (
                <li key={i}>• {risk}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Financial Section */}
      <Section title="Fundamental Analysis">
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <MetricCard
            title="Valuation"
            items={[
              ["Market Cap", formatNum(financial.market_cap)],
              ["P/E Ratio", financial.pe_ratio?.toFixed(2) || "N/A"],
              ["Forward P/E", financial.forward_pe?.toFixed(2) || "N/A"],
              ["P/B Ratio", financial.pb_ratio?.toFixed(2) || "N/A"],
              ["PEG Ratio", financial.peg_ratio?.toFixed(2) || "N/A"],
            ]}
          />
          <MetricCard
            title="Profitability"
            items={[
              ["Revenue", formatNum(financial.revenue)],
              ["Revenue Growth", formatPct(financial.revenue_growth)],
              ["Profit Margin", formatPct(financial.profit_margin)],
              ["Operating Margin", formatPct(financial.operating_margin)],
              ["ROE", formatPct(financial.roe)],
            ]}
          />
        </div>
        <AnalysisText text={report.financial.analysis} />
      </Section>

      {/* Technical Section */}
      <Section title="Technical Analysis">
        <div className="mb-6">
          <PriceChart
            ticker={report.ticker}
            currentPrice={financial.current_price}
            support={technical.support_level}
            resistance={technical.resistance_level}
          />
        </div>
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <MetricCard
            title="Indicators"
            items={[
              ["Trend", technical.trend],
              ["SMA-50", `$${technical.sma_50?.toFixed(2)}`],
              ["SMA-200", `$${technical.sma_200?.toFixed(2) || "N/A"}`],
              ["RSI (14)", technical.rsi_14?.toFixed(2)],
              ["MACD Histogram", technical.macd_histogram?.toFixed(4)],
            ]}
          />
          <MetricCard
            title="Key Levels"
            items={[
              ["Support", `$${technical.support_level?.toFixed(2)}`],
              ["Resistance", `$${technical.resistance_level?.toFixed(2)}`],
              ["52-Week High", `$${financial.week_52_high?.toFixed(2)}`],
              ["52-Week Low", `$${financial.week_52_low?.toFixed(2)}`],
              ["Golden Cross", technical.golden_cross ? "Yes" : "No"],
            ]}
          />
        </div>
        <AnalysisText text={report.technical.analysis} />
      </Section>

      {/* Competitor Section */}
      <Section title="Competitive Positioning">
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-sm">
            <thead className="bg-primary-500 text-white">
              <tr>
                <th className="text-left p-3">Ticker</th>
                <th className="text-left p-3">Company</th>
                <th className="text-right p-3">Market Cap</th>
                <th className="text-right p-3">P/E</th>
                <th className="text-right p-3">Rev Growth</th>
                <th className="text-right p-3">Margin</th>
              </tr>
            </thead>
            <tbody>
              <tr className="bg-amber-50 font-semibold border-b border-slate-200">
                <td className="p-3">{report.ticker}</td>
                <td className="p-3">{report.company_name}</td>
                <td className="p-3 text-right">
                  {formatNum(financial.market_cap)}
                </td>
                <td className="p-3 text-right">
                  {financial.pe_ratio?.toFixed(2)}
                </td>
                <td className="p-3 text-right">
                  {formatPct(financial.revenue_growth)}
                </td>
                <td className="p-3 text-right">
                  {formatPct(financial.profit_margin)}
                </td>
              </tr>
              {competitor.competitors?.map((c) => (
                <tr key={c.ticker} className="border-b border-slate-100">
                  <td className="p-3">{c.ticker}</td>
                  <td className="p-3">{c.company_name}</td>
                  <td className="p-3 text-right">{formatNum(c.market_cap)}</td>
                  <td className="p-3 text-right">{c.pe_ratio?.toFixed(2)}</td>
                  <td className="p-3 text-right">
                    {formatPct(c.revenue_growth)}
                  </td>
                  <td className="p-3 text-right">
                    {formatPct(c.profit_margin)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <AnalysisText text={competitor.competitive_position} />
      </Section>

      {/* News Section */}
      <Section title="News Sentiment">
        <div className="mb-4 flex items-center gap-4 flex-wrap">
          <span className="text-sm text-slate-600">Overall:</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              news.overall_sentiment === "Positive"
                ? "bg-green-100 text-green-800"
                : news.overall_sentiment === "Negative"
                  ? "bg-red-100 text-red-800"
                  : "bg-slate-100 text-slate-800"
            }`}
          >
            {news.overall_sentiment}
          </span>
          <span className="text-sm text-slate-600">
            {news.positive_count} positive • {news.negative_count} negative •{" "}
            {news.neutral_count} neutral
          </span>
        </div>
        <p className="text-slate-700 mb-4">{news.analysis_summary}</p>
        <div className="space-y-2">
          {news.articles?.slice(0, 10).map((article, i) => (
            <div
              key={i}
              className={`p-3 border-l-4 rounded text-sm ${sentimentColors[article.sentiment] || sentimentColors["Neutral"]}`}
            >
              <p className="font-medium text-slate-900">{article.title}</p>
              <p className="text-xs text-slate-500 mt-1">
                {article.source} • {article.published_at?.slice(0, 10)}
              </p>
              {article.summary && (
                <p className="text-xs text-slate-600 mt-1">{article.summary}</p>
              )}
            </div>
          ))}
        </div>
      </Section>

      {/* Footer info */}
      <div className="text-center text-xs text-slate-400 pt-4">
        Analysis completed in {report.total_time_seconds}s • Generated by finAG
        AI
      </div>
    </div>
  );
}

// Helper components
function Section({ title, children }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h2 className="text-xl font-bold text-primary-600 border-b border-slate-200 pb-2 mb-4">
        {title}
      </h2>
      {children}
    </div>
  );
}

function MetricCard({ title, items }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-700 mb-2">{title}</h3>
      <table className="w-full text-sm">
        <tbody>
          {items.map(([label, value], i) => (
            <tr key={i} className="border-b border-slate-100 last:border-0">
              <td className="py-1.5 text-slate-600">{label}</td>
              <td className="py-1.5 text-right font-medium text-slate-900">
                {value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AnalysisText({ text }) {
  return (
    <div className="prose prose-sm max-w-none text-slate-700 whitespace-pre-wrap">
      {text}
    </div>
  );
}

export default ReportView;
