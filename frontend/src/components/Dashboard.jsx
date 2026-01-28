import { useState, useEffect } from 'react';
import StockChart from './StockChart';
import StatsGrid from './StatsGrid';
import { RefreshCw, ArrowUp, ArrowDown, ExternalLink, Star } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { addToWatchlist, removeFromWatchlist, getWatchlist } from '../supabase';

const TimeSelector = ({ activeRange, onSelect }) => {
    const ranges = ["1W", "1M", "3M", "6M", "1Y", "MAX"];
    return (
        <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-md">
            {ranges.map((range) => (
                <button
                    key={range}
                    onClick={() => onSelect(range)}
                    className={`px-3 py-1 text-xs font-medium rounded transition-all ${
                        activeRange === range
                        ? 'bg-white dark:bg-gray-600 shadow text-black dark:text-white'
                        : 'text-gray-500 hover:text-gray-900 dark:hover:text-gray-300'
                    }`}
                >
                    {range}
                </button>
            ))}
        </div>
    );
};

const SentimentBadge = ({ score }) => {
    let color = 'bg-gray-500';
    let label = 'Neutral';
    
    if (score >= 0.5) { color = 'bg-[#0ecb81]'; label = 'Strong Buy'; }
    else if (score >= 0.2) { color = 'bg-green-500'; label = 'Buy'; }
    else if (score <= -0.5) { color = 'bg-[#f6465d]'; label = 'Strong Sell'; }
    else if (score <= -0.2) { color = 'bg-red-500'; label = 'Sell'; }

    return (
        <span className={`${color} text-white text-xs font-bold px-2 py-1 rounded uppercase`}>
            {label} ({score})
        </span>
    );
};

function Dashboard({ data, ticker, onRangeChange, onRefresh, isLoading }) {
    const { current_sentiment, graph_data, news, quant_analysis } = data;
    const latest = graph_data && graph_data.length > 0 ? graph_data[graph_data.length - 1] : { price: 0 };
    const prev = graph_data && graph_data.length > 1 ? graph_data[graph_data.length - 2] : latest;
    
    const priceChange = latest.price - prev.price;
    const percentChange = (priceChange / prev.price) * 100;
    const isUp = priceChange >= 0;

    const [timeRange, setTimeRange] = useState("1W");
    
    // Watchlist Logic
    const { user } = useAuth();
    const [isWatchlisted, setIsWatchlisted] = useState(false);
    const [wLoading, setWLoading] = useState(false);

    useEffect(() => {
        if (user && ticker) {
            getWatchlist(user.id).then(({ data }) => {
                if (data) {
                    const found = data.find(item => item.ticker === ticker.toUpperCase());
                    setIsWatchlisted(!!found);
                }
            });
        }
    }, [user, ticker]);

    const toggleWatchlist = async () => {
        if (!user) return; // Should show auth modal ideally
        setWLoading(true);
        if (isWatchlisted) {
            await removeFromWatchlist(user.id, ticker);
            setIsWatchlisted(false);
        } else {
            await addToWatchlist(user.id, ticker);
            setIsWatchlisted(true);
        }
        setWLoading(false);
    };

    const handleRangeSelect = (range) => {
        if (range === timeRange) return;
        setTimeRange(range);
        if (onRangeChange) onRangeChange(range);
    };

    return (
        <div className="animate-fade-in space-y-4">
            {/* Header Strip */}
            <div className="card flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{ticker}</h1>
                        <span className="text-xs px-2 py-0.5 rounded bg-gray-200 dark:bg-gray-700 font-mono" style={{ color: 'var(--text-secondary)' }}>
                            Stock / USD
                        </span>
                        {/* Star Button */}
                        {user && (
                            <button 
                                onClick={toggleWatchlist} 
                                disabled={wLoading}
                                className={`p-1.5 rounded-full transition-all ${isWatchlisted ? 'bg-[var(--accent-color)] text-black' : 'bg-gray-100 dark:bg-gray-800 text-gray-400 hover:text-[var(--accent-color)]'}`}
                                title={isWatchlisted ? "Remove from Watchlist" : "Add to Watchlist"}
                            >
                                <Star className={`w-4 h-4 ${isWatchlisted ? 'fill-black' : ''} ${wLoading ? 'animate-pulse' : ''}`} />
                            </button>
                        )}
                    </div>
                    <div className="flex items-baseline gap-3 mt-1">
                        <span className={`text-3xl font-bold ${isUp ? 'text-[var(--color-up)]' : 'text-[var(--color-down)]'}`}>
                            ${latest.price.toFixed(2)}
                        </span>
                        <span className={`flex items-center text-sm font-medium ${isUp ? 'text-[var(--color-up)]' : 'text-[var(--color-down)]'}`}>
                            {isUp ? <ArrowUp className="w-3 h-3 mr-1" /> : <ArrowDown className="w-3 h-3 mr-1" />}
                            {Math.abs(priceChange).toFixed(2)} ({Math.abs(percentChange).toFixed(2)}%)
                        </span>
                    </div>
                </div>
                
                <div className="flex items-center gap-4">
                    <div className="text-right hidden sm:block">
                        <div className="text-xs text-gray-500 uppercase">Sentiment</div>
                        <SentimentBadge score={quant_analysis?.final_score || 0} />
                    </div>
                     <div className="text-right hidden sm:block">
                        <div className="text-xs text-gray-500 uppercase">AI Confidence</div>
                        <div className="text-sm font-bold text-[var(--accent-color)]">
                            {(quant_analysis?.neural_analysis?.confidence * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                
                {/* Chart Section (2/3) */}
                <div className="lg:col-span-2 card min-h-[500px] flex flex-col">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>Price Chart</h3>
                        <TimeSelector activeRange={timeRange} onSelect={handleRangeSelect} />
                    </div>
                    <div className="flex-1 bg-gray-50 dark:bg-[#161a1e] rounded-lg border border-dashed dark:border-gray-800 p-2 relative">
                         {isLoading && (
                            <div className="absolute inset-0 z-10 bg-white/50 dark:bg-black/50 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--accent-color)]"></div>
                            </div>
                        )}
                        <StockChart data={graph_data} />
                    </div>
                </div>

                {/* Right Column: Stats & News (1/3) */}
                <div className="space-y-4">
                    {/* Market Stats */}
                    <div className="card">
                        <h3 className="font-semibold mb-3 border-b pb-2 dark:border-gray-700" style={{ color: 'var(--text-primary)' }}>Market Stats</h3>
                        <StatsGrid data={graph_data} />
                    </div>

                    {/* AI Insight Box */}
                    <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-100 dark:border-blue-800">
                        <h3 className="text-sm font-bold text-blue-600 dark:text-blue-400 mb-2 uppercase tracking-wide">
                            AI Signal
                        </h3>
                        <p className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
                            {quant_analysis?.signal || "Neutral"}
                        </p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                            Based on {news?.length || 0} analyzed news points and technical indicators.
                        </p>
                    </div>

                    {/* News Feed (Compact) */}
                    <div className="card flex-1 max-h-[400px] flex flex-col">
                        <div className="flex justify-between items-center mb-3 pb-2 border-b dark:border-gray-700">
                            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Latest News</h3>
                            <button onClick={onRefresh} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors">
                                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>
                        <div className="overflow-y-auto custom-scrollbar flex-1 space-y-3 pr-1">
                            {news && news.length > 0 ? (
                                news.map((item, idx) => (
                                    <div key={idx} className="group cursor-pointer">
                                        <div className="flex justify-between items-start">
                                            <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:text-[var(--accent-color)] transition-colors line-clamp-2" style={{ color: 'var(--text-primary)' }}>
                                                {item.title}
                                            </a>
                                            <span className={`text-[10px] px-1.5 py-0.5 rounded ml-2 whitespace-nowrap ${item.sentiment > 0 ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                                                {item.sentiment.toFixed(2)}
                                            </span>
                                        </div>
                                        <div className="flex justify-between mt-1">
                                            <span className="text-[10px] text-gray-400">{item.publisher}</span>
                                            <span className="text-[10px] text-gray-500">{new Date(item.published).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-sm text-center py-4 text-gray-500">No news available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;