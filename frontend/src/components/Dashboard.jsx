import { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import StockChart from './StockChart';
import StatsGrid from './StatsGrid';
import { RefreshCw, ArrowUp, ArrowDown, Star, Activity, Zap, Shield, TrendingUp, LayoutTemplate, LineChart, Brain, Newspaper as NewsIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { addToWatchlist, removeFromWatchlist, getWatchlist } from '../supabase';
import LoadingSpinner from './LoadingSpinner';

const API_URL = 'http://127.0.0.1:5000';

const TimeSelector = ({ activeRange, onSelect }) => {
    const ranges = ["1W", "1M", "3M", "6M", "YTD", "1Y", "MAX"];
    return (
        <div className="flex bg-[var(--bg-secondary)] rounded-lg p-1">
            {ranges.map((range) => (
                <button
                    key={range}
                    onClick={() => onSelect(range)}
                    className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${
                        activeRange === range
                        ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                    }`}
                >
                    {range}
                </button>
            ))}
        </div>
    );
};

function Dashboard() {
    const { ticker } = useParams();
    const [searchParams] = useSearchParams();
    const companyName = searchParams.get('name');
    
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [timeRange, setTimeRange] = useState("6M");
    const [chartType, setChartType] = useState('simple'); 
    
    const { user } = useAuth();
    const [isWatchlisted, setIsWatchlisted] = useState(false);
    const [wLoading, setWLoading] = useState(false);

    useEffect(() => {
        if (ticker) {
            fetchStockData(ticker, timeRange, false, companyName);
        }
    }, [ticker, timeRange]);

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

    const fetchStockData = async (tickerSymbol, range = '1W', force = false, cName = null) => {
        setLoading(true);
        setError('');
        try {
            const url = `${API_URL}/api/analyze?ticker=${tickerSymbol}&range=${range}&force=${force}&name=${encodeURIComponent(cName || '')}`;
            const response = await fetch(url);
    
            if (!response.ok) {
                let errorMessage = `Server Error (${response.status})`;
                try {
                    const errorData = await response.json();
                    if (errorData.error) errorMessage = errorData.error;
                } catch (e) {
                    if (response.statusText) errorMessage = response.statusText;
                }
                throw new Error(errorMessage);
            }
    
            const result = await response.json();
            if (result.error) {
                setError(result.error);
            } else {
                setData(result);
            }
        } catch (err) {
            console.error("Fetch Error:", err);
            setError(err.message || "Failed to connect to server.");
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = () => {
        fetchStockData(ticker, timeRange, true, companyName);
    };

    const toggleWatchlist = async () => {
        if (!user) return; 
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

    if (loading && !data) {
        return <div className="flex flex-col items-center justify-center h-full w-full"><LoadingSpinner /></div>;
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-6 py-4 rounded-lg text-center">
                    <span className="font-bold block text-lg mb-2">Analysis Failed</span>
                    <span>{error}</span>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const { current_sentiment, graph_data, news, quant_analysis } = data;
    const latest = graph_data && graph_data.length > 0 ? graph_data[graph_data.length - 1] : { price: 0 };
    const prev = graph_data && graph_data.length > 1 ? graph_data[graph_data.length - 2] : latest;
    
    const priceChange = latest.price - prev.price;
    const percentChange = (priceChange / prev.price) * 100;
    const isUp = priceChange >= 0;
    const colorClass = isUp ? 'text-[var(--color-up)]' : 'text-[var(--color-down)]';

    const deepInsight = quant_analysis?.deep_insight || {};
    const neural = quant_analysis?.neural_analysis || {};
    // Use System-Wide Confidence (Weighted Average) instead of just LSTM
    const confidence = quant_analysis?.confidence || 0;

    const experts = quant_analysis?.expert_opinion || {};
    const xgb = experts.xgboost || { signal: "Neutral", probability: 0 };
    const lstm = experts.lstm || { signal: "Neutral", confidence: 0 };
    const sentimentExpert = experts.sentiment || { label: "Neutral", score: 0 };

    return (
        <div className="flex flex-col h-full bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans overflow-y-auto">
            
            {/* 1. Modern Financial Header */}
            <div className="px-6 py-6 border-b border-[var(--border-color)] bg-[var(--bg-card)]">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <div className="flex items-baseline gap-3 mb-1">
                            <h1 className="text-3xl font-extrabold tracking-tight">{ticker}</h1>
                            <span className="text-lg text-[var(--text-secondary)] font-medium">{companyName || "Stock Analysis"}</span>
                            {user && (
                                <button onClick={toggleWatchlist} disabled={wLoading} className="ml-2 hover:scale-110 transition-transform">
                                    <Star className={`w-6 h-6 ${isWatchlisted ? 'fill-yellow-400 text-yellow-400' : 'text-[var(--text-secondary)]'}`} />
                                </button>
                            )}
                        </div>
                        <div className="flex items-center gap-4">
                            <span className={`text-4xl font-bold ${colorClass}`}>
                                ${latest.price.toFixed(2)}
                            </span>
                            <div className={`flex items-center text-lg font-semibold ${colorClass}`}>
                                {isUp ? <ArrowUp className="w-5 h-5 mr-1" /> : <ArrowDown className="w-5 h-5 mr-1" />}
                                {Math.abs(priceChange).toFixed(2)} ({Math.abs(percentChange).toFixed(2)}%)
                            </div>
                            <span className="text-xs text-[var(--text-secondary)] uppercase tracking-wider mt-2">At Close</span>
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                        <button onClick={handleRefresh} className="flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--bg-secondary)] hover:bg-[var(--border-color)] transition-colors text-sm font-bold">
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            Refresh Data
                        </button>
                    </div>
                </div>
            </div>

            {/* 2. Main Content Grid */}
            <div className="flex-1 max-w-7xl mx-auto w-full p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                {/* LEFT COLUMN (Chart & News) - Spans 8 cols */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    
                    {/* CHART CARD */}
                    <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] shadow-sm overflow-hidden">
                        <div className="p-4 border-b border-[var(--border-color)] flex flex-wrap justify-between items-center gap-4">
                            <div className="flex gap-2">
                                <button 
                                    onClick={() => setChartType('simple')}
                                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-bold transition-colors ${chartType === 'simple' ? 'bg-[var(--accent-color)] text-black' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]'}`}
                                >
                                    <LineChart className="w-4 h-4" /> Simple
                                </button>
                                <button 
                                    onClick={() => setChartType('pro')}
                                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-bold transition-colors ${chartType === 'pro' ? 'bg-[var(--accent-color)] text-black' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]'}`}
                                >
                                    <LayoutTemplate className="w-4 h-4" /> Pro
                                </button>
                            </div>
                            <TimeSelector activeRange={timeRange} onSelect={setTimeRange} />
                        </div>
                        <div className="p-4 h-[450px]">
                            <StockChart data={graph_data} chartType={chartType} />
                        </div>
                    </div>

                    {/* NEWS FEED */}
                    <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] shadow-sm p-6">
                        <div className="flex items-center gap-2 mb-6">
                            <NewsIcon className="w-6 h-6 text-[var(--accent-color)]" />
                            <h2 className="text-xl font-bold">Latest News ({news?.length || 0})</h2>
                        </div>
                        <div className="space-y-4">
                            {news && news.length > 0 ? (
                                news.map((item, idx) => (
                                    <a key={idx} href={item.link} target="_blank" rel="noopener noreferrer" className="group block">
                                        <div className="flex gap-4">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-xs font-bold text-[var(--text-secondary)] uppercase">{item.publisher}</span>
                                                    <span className="text-xs text-[var(--text-secondary)]">•</span>
                                                    <span className="text-xs text-[var(--text-secondary)]">{item.published}</span>
                                                </div>
                                                <h3 className="text-base font-bold group-hover:text-[var(--accent-color)] transition-colors leading-snug mb-2">
                                                    {item.title}
                                                </h3>
                                                <div className="flex gap-2">
                                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${item.sentiment > 0 ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                                                        {item.sentiment > 0 ? 'Positive' : 'Negative'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                ))
                            ) : (
                                <p className="text-[var(--text-secondary)] text-center py-4">No recent news available.</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* RIGHT COLUMN (AI & Stats) - Spans 4 cols */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    
                    {/* AI INTELLIGENCE CARD */}
                    <div className="relative bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-secondary)] rounded-2xl border border-[var(--border-color)] shadow-md overflow-hidden group">
                        <div className="absolute top-0 left-0 w-full h-1 bg-[var(--accent-color)]"></div>
                        <div className="p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <div className="p-2 rounded-lg bg-[var(--accent-color)] text-black">
                                    <Brain className="w-6 h-6" />
                                </div>
                                <h2 className="text-lg font-bold uppercase tracking-wide">Prism AI</h2>
                            </div>

                            <div className="text-center py-4 mb-4">
                                <div className="text-sm text-[var(--text-secondary)] mb-1">Recommendation</div>
                                <div className={`text-3xl font-black ${quant_analysis?.signal?.includes("BUY") ? 'text-[var(--color-up)]' : quant_analysis?.signal?.includes("SELL") ? 'text-[var(--color-down)]' : 'text-gray-400'}`}>
                                    {quant_analysis?.signal || "NEUTRAL"}
                                </div>
                                <div className="flex justify-center gap-4 mt-2">
                                    <span className="text-xs font-bold text-[var(--text-secondary)]">
                                        Score: <span className="text-[var(--text-primary)]">{quant_analysis?.final_score > 0 ? '+' : ''}{quant_analysis?.final_score?.toFixed(0)}</span>
                                    </span>
                                    <span className="text-xs font-bold text-[var(--text-secondary)]">
                                        Conf: <span className="text-[var(--text-primary)]">{(confidence * 100).toFixed(1)}%</span>
                                    </span>
                                </div>
                            </div>

                            {/* Advisors List */}
                            <div className="space-y-3 mb-6">
                                <div className="flex justify-between items-center p-3 rounded-xl bg-[var(--bg-primary)] border border-[var(--border-color)]">
                                    <div className="flex flex-col">
                                        <span className="text-xs font-bold">Quant (XGB)</span>
                                        <span className="text-[10px] text-[var(--text-secondary)]">Score: {xgb.score}</span>
                                    </div>
                                    <span className={`text-xs font-bold ${xgb.signal === 'Bullish' ? 'text-[var(--color-up)]' : 'text-[var(--color-down)]'}`}>
                                        {xgb.signal} ({xgb.probability}%)
                                    </span>
                                </div>
                                <div className="flex justify-between items-center p-3 rounded-xl bg-[var(--bg-primary)] border border-[var(--border-color)]">
                                    <div className="flex flex-col">
                                        <span className="text-xs font-bold">Pattern (LSTM)</span>
                                        <span className="text-[10px] text-[var(--text-secondary)]">Trend Analysis</span>
                                    </div>
                                    <span className={`text-xs font-bold ${lstm.signal === 'Bullish' ? 'text-[var(--color-up)]' : 'text-[var(--color-down)]'}`}>
                                        {lstm.signal} ({lstm.confidence}%)
                                    </span>
                                </div>
                                <div className="flex justify-between items-center p-3 rounded-xl bg-[var(--bg-primary)] border border-[var(--border-color)]">
                                    <div className="flex flex-col">
                                        <span className="text-xs font-bold">Sentiment</span>
                                        <span className="text-[10px] text-[var(--text-secondary)]">Score: {sentimentExpert.score}</span>
                                    </div>
                                    <span className={`text-xs font-bold ${sentimentExpert.score > 50 ? 'text-[var(--color-up)]' : sentimentExpert.score < 50 ? 'text-[var(--color-down)]' : 'text-[var(--text-secondary)]'}`}>
                                        {sentimentExpert.label}
                                    </span>
                                </div>
                            </div>

                            <div className="bg-[var(--bg-primary)] p-4 rounded-xl border border-[var(--border-color)]">
                                <div className="flex items-center gap-2 mb-2 text-[var(--accent-color)]">
                                    <Zap className="w-4 h-4" />
                                    <span className="text-xs font-bold uppercase">AI Strategy</span>
                                </div>
                                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                    {deepInsight.strategy || "Monitoring market conditions for clear signals."}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* KEY STATISTICS */}
                    <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] shadow-sm p-6">
                        <h3 className="text-lg font-bold mb-4">Key Statistics</h3>
                        <StatsGrid data={graph_data} />
                        
                        <div className="mt-6 pt-4 border-t border-[var(--border-color)]">
                            <div className="flex justify-between items-center text-xs text-[var(--text-secondary)]">
                                <span>Support</span>
                                <span className="font-mono text-[var(--color-up)]">${deepInsight.support_level?.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between items-center text-xs text-[var(--text-secondary)] mt-2">
                                <span>Resistance</span>
                                <span className="font-mono text-[var(--color-down)]">${deepInsight.resistance_level?.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default Dashboard;
