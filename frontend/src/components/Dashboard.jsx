/**
 * Dashboard Component
 * Clean, Spacious Grid Layout
 */

import { useState } from 'react';
import StockChart from './StockChart';
import StatsGrid from './StatsGrid';
import SentimentGauge from './SentimentGauge';
import { TrendingUp, Loader2, Database, FileText, Scissors, AlertTriangle, CheckCircle } from 'lucide-react';

/* Internal TimeSelector Component */
const TimeSelector = ({ activeRange, onSelect }) => {
    const ranges = ["1W", "1M", "3M", "6M", "1Y", "MAX"];

    return (
        <div className="flex gap-2 mb-4 bg-black/20 p-1 rounded-lg w-fit">
            {ranges.map((range) => (
                <button
                    key={range}
                    onClick={() => onSelect(range)}
                    className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-all ${activeRange === range
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                        }`}
                >
                    {range}
                </button>
            ))}
        </div>
    );
};

/* Debug Stats Component */
const DebugStats = ({ debug }) => {
    if (!debug) return null;
    const { total, full_text, snippet, timeouts } = debug;

    return (
        <div className="mt-8 bg-black/40 border border-white/5 rounded-2xl p-4 text-xs font-mono">
            <h4 className="flex items-center gap-2 text-gray-400 mb-2 uppercase tracking-widest font-bold">
                <Database className="w-3 h-3" /> Scraping Debug Stats
            </h4>
            <div className="grid grid-cols-4 gap-4 text-center">
                <div className="bg-white/5 p-2 rounded">
                    <span className="block text-xl font-bold text-white">{total}</span>
                    <span className="text-gray-500">Total</span>
                </div>
                <div className="bg-green-500/10 p-2 rounded border border-green-500/20">
                    <span className="block text-xl font-bold text-green-400">{full_text}</span>
                    <span className="text-green-600/70">Full Text</span>
                </div>
                <div className="bg-yellow-500/10 p-2 rounded border border-yellow-500/20">
                    <span className="block text-xl font-bold text-yellow-400">{snippet}</span>
                    <span className="text-yellow-600/70">Snippets</span>
                </div>
                <div className="bg-red-500/10 p-2 rounded border border-red-500/20">
                    <span className="block text-xl font-bold text-red-400">{timeouts}</span>
                    <span className="text-red-600/70">Timeouts</span>
                </div>
            </div>
            <div className="mt-2 text-gray-600 text-center italic">
                Timeout threshold: 1.5s per article
            </div>
        </div>
    );
};

function Dashboard({ data, ticker, onRangeChange, isLoading }) {
    const { current_sentiment, graph_data, news, debug } = data;
    const latestPrice = graph_data && graph_data.length > 0 ? graph_data[graph_data.length - 1].price : 0;
    const [timeRange, setTimeRange] = useState("1W");
    const [showDebug, setShowDebug] = useState(true);

    // Helpers
    const getSentimentColor = (score) => {
        if (score >= 0.2) return 'text-green-400';
        if (score <= -0.2) return 'text-red-400';
        return 'text-yellow-400';
    };

    const getSentimentBg = (score) => {
        if (score >= 0.2) return 'bg-green-500/20 border-green-500/30';
        if (score <= -0.2) return 'bg-red-500/20 border-red-500/30';
        return 'bg-yellow-500/20 border-yellow-500/30';
    };

    const handleRangeSelect = (range) => {
        if (range === timeRange) return;
        setTimeRange(range);
        if (onRangeChange) {
            onRangeChange(range);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">

            {/* LEFT COLUMN: Stats & Chart (Takes 2/3 width) */}
            <div className="lg:col-span-2 space-y-8">

                {/* Top Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Price Card & Stats */}
                    <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-6 shadow-xl relative overflow-hidden group hover:bg-white/10 transition-colors col-span-1 md:col-span-2 lg:col-span-1">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <TrendingUp className="w-24 h-24 text-blue-400" />
                        </div>

                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">Ticker Symbol</h3>
                                <div className="flex items-baseline gap-2">
                                    <h2 className="text-4xl font-bold text-white">{ticker}</h2>
                                </div>
                                <div className="mt-4">
                                    <span className="text-3xl font-mono text-blue-300">${latestPrice.toFixed(2)}</span>
                                    <span className="text-gray-400 text-sm ml-2">Current Price</span>
                                </div>
                            </div>
                        </div>

                        {/* Feature B: Stats Grid inside Ticker Card */}
                        <div className="mt-6 border-t border-white/5 pt-4">
                            <StatsGrid data={graph_data} />
                        </div>
                    </div>

                    {/* Sentiment Score Card */}
                    <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-6 shadow-xl relative overflow-hidden transition-colors flex flex-col justify-center min-h-[250px]">
                        <SentimentGauge score={data.quant_analysis?.final_score || 0} />
                    </div>
                </div>

                {/* Main Chart Section */}
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 shadow-xl min-h-[460px]">
                    <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
                        <h3 className="text-xl font-bold text-gray-200 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-purple-400" />
                            Price History
                        </h3>
                        <TimeSelector activeRange={timeRange} onSelect={handleRangeSelect} />
                    </div>

                    {isLoading ? (
                        <div className="h-[300px] w-full flex flex-col items-center justify-center text-gray-400">
                            <Loader2 className="w-10 h-10 text-purple-400 animate-spin mb-4" />
                            <p>Fetching {timeRange} data...</p>
                        </div>
                    ) : (
                        <StockChart data={graph_data} />
                    )}

                </div>

                {/* Debug Stats Footer */}
                {showDebug && <DebugStats debug={debug} />}

            </div>

            {/* RIGHT COLUMN: News Feed (Takes 1/3 width) */}
            <div className="lg:col-span-1">
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-6 shadow-xl h-full">
                    <h3 className="text-xl font-bold text-gray-200 mb-6 border-b border-white/10 pb-4">
                        Latest Market News
                    </h3>

                    <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                        {news && news.length > 0 ? (
                            news.map((item, idx) => (
                                <div key={idx} className="group p-4 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-purple-500/30 transition-all cursor-pointer relative overflow-hidden">
                                    {/* Debug Source Badge */}
                                    {item.debug && (
                                        <div className="absolute top-2 right-2 flex gap-1">
                                            {item.debug.content_source === 'full_text' ? (
                                                <div className="bg-green-500/10 text-green-400 p-1 rounded" title="Full Text Analyzed">
                                                    <FileText className="w-3 h-3" />
                                                </div>
                                            ) : (
                                                <div className="bg-yellow-500/10 text-yellow-400 p-1 rounded" title="Snippet Fallback">
                                                    <Scissors className="w-3 h-3" />
                                                </div>
                                            )}
                                            {item.debug.scrape_status === 'timeout' && (
                                                <div className="bg-red-500/10 text-red-400 p-1 rounded" title="Request Timed Out">
                                                    <AlertTriangle className="w-3 h-3" />
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    <div className="flex justify-between items-start mb-2 gap-3">
                                        <span className="text-xs font-mono text-purple-300">
                                            {new Date(item.published).toLocaleDateString()}
                                        </span>
                                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${item.sentiment > 0.2 ? 'bg-green-500/20 text-green-300' :
                                            item.sentiment < -0.2 ? 'bg-red-500/20 text-red-300' :
                                                'bg-gray-500/20 text-gray-300'
                                            }`}>
                                            {item.sentiment.toFixed(2)}
                                        </span>
                                    </div>
                                    <h4 className="text-gray-200 font-medium leading-snug group-hover:text-white transition-colors pr-6">
                                        {item.title}
                                    </h4>
                                    <div className="mt-3 flex items-center justify-between">
                                        <span className="text-xs text-gray-500 uppercase tracking-wider truncate max-w-[70%]">{item.publisher || 'Unknown Source'}</span>
                                        {item.debug && <span className="text-[10px] text-gray-600 font-mono">{(item.debug.time_taken || 0).toFixed(2)}s</span>}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-gray-500 text-center py-10">
                                No news available.
                            </div>
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
}

export default Dashboard;
