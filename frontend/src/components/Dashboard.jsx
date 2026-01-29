import { useState, useEffect } from 'react';
import StockChart from './StockChart';
import StatsGrid from './StatsGrid';
import { RefreshCw, ArrowUp, ArrowDown, Star, Activity, Zap, Shield, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { addToWatchlist, removeFromWatchlist, getWatchlist } from '../supabase';

const TimeSelector = ({ activeRange, onSelect }) => {
    const ranges = ["1W", "1M", "3M", "6M", "1Y", "MAX"];
    return (
        <div className="flex gap-1 bg-[#2b3139] p-0.5 rounded text-[10px]">
            {ranges.map((range) => (
                <button
                    key={range}
                    onClick={() => onSelect(range)}
                    className={`px-2 py-0.5 font-medium rounded transition-colors ${
                        activeRange === range
                        ? 'bg-[#848e9c] text-[#161a1e]'
                        : 'text-[#848e9c] hover:text-white'
                    }`}
                >
                    {range}
                </button>
            ))}
        </div>
    );
};

function Dashboard({ data, ticker, onRangeChange, onRefresh, isLoading }) {
    const { current_sentiment, graph_data, news, quant_analysis } = data;
    const latest = graph_data && graph_data.length > 0 ? graph_data[graph_data.length - 1] : { price: 0 };
    const prev = graph_data && graph_data.length > 1 ? graph_data[graph_data.length - 2] : latest;
    
    const priceChange = latest.price - prev.price;
    const percentChange = (priceChange / prev.price) * 100;
    const isUp = priceChange >= 0;
    const colorClass = isUp ? 'text-[#0ecb81]' : 'text-[#f6465d]';

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

    const handleRangeSelect = (range) => {
        if (range === timeRange) return;
        setTimeRange(range);
        if (onRangeChange) onRangeChange(range);
    };

    // Parse Quant Data
    const deepInsight = quant_analysis?.deep_insight || {};
    const strategy = deepInsight.strategy || "Neutral";
    const support = deepInsight.support_level || 0;
    const resistance = deepInsight.resistance_level || 0;
    const instFlow = deepInsight.institutional_flow || "Neutral";
    
    const neural = quant_analysis?.neural_analysis || {};
    const confidence = neural.confidence || 0;

    const breakdown = quant_analysis?.breakdown || {};

    const experts = quant_analysis?.expert_opinion || {};
    const xgb = experts.xgboost || { signal: "Neutral", probability: 0 };
    const lstm = experts.lstm || { signal: "Neutral", confidence: 0 };
    const sentimentExpert = experts.sentiment || { label: "Neutral", score: 0 };

    return (
        <div className="flex flex-col h-full bg-[#161a1e] text-[#eaecef] font-sans">
            {/* 1. Header Bar (Binance Style) */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#1e2329] border-b border-[#2b3139]">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-bold text-white tracking-wide">{ticker}</h1>
                        <span className="text-xs text-[#848e9c]">/USDT</span>
                         {user && (
                            <button onClick={toggleWatchlist} disabled={wLoading}>
                                <Star className={`w-4 h-4 ${isWatchlisted ? 'fill-[#f0b90b] text-[#f0b90b]' : 'text-[#848e9c]'}`} />
                            </button>
                        )}
                    </div>
                    
                    <div className="flex flex-col">
                        <span className={`text-lg font-mono font-medium ${colorClass}`}>
                            {latest.price.toFixed(2)}
                        </span>
                        <span className="text-xs text-[#848e9c]">Price</span>
                    </div>

                    <div className="flex flex-col">
                        <span className={`text-sm font-medium ${colorClass}`}>
                            {isUp ? '+' : ''}{priceChange.toFixed(2)} ({percentChange.toFixed(2)}%)
                        </span>
                        <span className="text-xs text-[#848e9c]">24h Change</span>
                    </div>

                    <div className="hidden md:flex flex-col">
                        <span className="text-sm font-medium text-white">{strategy}</span>
                        <span className="text-xs text-[#848e9c]">AI Strategy</span>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                     <button onClick={onRefresh} className="p-2 hover:bg-[#2b3139] rounded transition-colors text-[#848e9c]">
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* 2. Main Grid */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-1 p-1">
                
                {/* Left: Chart (Takes 3 cols) */}
                <div className="lg:col-span-3 flex flex-col gap-1">
                    {/* Chart Container */}
                    <div className="bg-[#1e2329] rounded p-1 flex-1 min-h-[500px] relative">
                        <div className="absolute top-2 right-2 z-10">
                            <TimeSelector activeRange={timeRange} onSelect={handleRangeSelect} />
                        </div>
                        {isLoading && (
                            <div className="absolute inset-0 z-20 bg-[#161a1e]/50 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#f0b90b]"></div>
                            </div>
                        )}
                        <StockChart data={graph_data} />
                    </div>
                    
                    {/* Bottom Stats / News */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-1 h-[300px]">
                        <div className="bg-[#1e2329] rounded p-3 overflow-y-auto custom-scrollbar">
                            <h3 className="text-sm font-bold text-[#eaecef] mb-3 sticky top-0 bg-[#1e2329]">Latest News</h3>
                            <div className="space-y-2">
                                {news && news.length > 0 ? (
                                    news.map((item, idx) => (
                                        <div key={idx} className="group cursor-pointer hover:bg-[#2b3139] p-2 rounded transition-colors">
                                            <div className="flex justify-between items-start">
                                                <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-[#eaecef] hover:text-[#f0b90b] line-clamp-2">
                                                    {item.title}
                                                </a>
                                            </div>
                                            <div className="flex justify-between mt-1 items-center">
                                                <span className="text-[10px] text-[#848e9c]">{item.publisher}</span>
                                                <span className={`text-[9px] px-1 rounded ${item.sentiment > 0 ? 'text-[#0ecb81] bg-[#0ecb81]/10' : 'text-[#f6465d] bg-[#f6465d]/10'}`}>
                                                    {item.sentiment > 0 ? 'BULLISH' : 'BEARISH'}
                                                </span>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-xs text-[#848e9c] text-center mt-10">No news available.</p>
                                )}
                            </div>
                        </div>
                        <div className="bg-[#1e2329] rounded p-3">
                             <h3 className="text-sm font-bold text-[#eaecef] mb-3">Market Stats</h3>
                             <StatsGrid data={graph_data} />
                        </div>
                    </div>
                </div>

                {/* Right: Quant Insight (Order Book Style) */}
                <div className="bg-[#1e2329] rounded p-4 flex flex-col gap-6 overflow-y-auto">
                    
                    <div>
                        <h2 className="text-[#f0b90b] text-sm font-bold uppercase tracking-wider mb-4 border-b border-[#2b3139] pb-2">
                            Deep Quant Insight
                        </h2>

                        <div className="space-y-4">
                            {/* Signal Card */}
                            <div className="bg-[#2b3139]/50 p-3 rounded border-l-2 border-[#f0b90b]">
                                <div className="text-xs text-[#848e9c] mb-1">Primary Signal</div>
                                <div className="text-xl font-bold text-white">{quant_analysis?.signal || "NEUTRAL"}</div>
                                <div className="flex items-center gap-2 mt-1">
                                    <div className="h-1.5 flex-1 bg-[#161a1e] rounded-full overflow-hidden">
                                        <div 
                                            className="h-full bg-[#f0b90b]" 
                                            style={{ width: `${confidence * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-xs text-[#f0b90b]">{(confidence * 100).toFixed(0)}% Conf.</span>
                                </div>
                            </div>

                            {/* Strategy */}
                            <div className="flex items-start gap-3">
                                <Activity className="w-5 h-5 text-[#848e9c] mt-0.5" />
                                <div>
                                    <div className="text-xs text-[#848e9c]">Detected Strategy</div>
                                    <div className="text-sm font-medium text-white">{strategy}</div>
                                </div>
                            </div>

                             {/* Inst Flow */}
                             <div className="flex items-start gap-3">
                                <TrendingUp className="w-5 h-5 text-[#848e9c] mt-0.5" />
                                <div>
                                    <div className="text-xs text-[#848e9c]">Inst. Flow</div>
                                    <div className={`text-sm font-medium ${instFlow.includes("Accumulation") ? 'text-[#0ecb81]' : instFlow.includes("Distribution") ? 'text-[#f6465d]' : 'text-white'}`}>
                                        {instFlow}
                                    </div>
                                </div>
                            </div>

                            {/* Levels */}
                            <div className="grid grid-cols-2 gap-2 mt-2">
                                <div className="bg-[#161a1e] p-2 rounded">
                                    <div className="text-[10px] text-[#848e9c] mb-1">Resistance</div>
                                    <div className="text-sm font-mono text-[#f6465d]">${resistance.toFixed(2)}</div>
                                </div>
                                <div className="bg-[#161a1e] p-2 rounded">
                                    <div className="text-[10px] text-[#848e9c] mb-1">Support</div>
                                    <div className="text-sm font-mono text-[#0ecb81]">${support.toFixed(2)}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* AI Board of Advisors (New) */}
                    <div>
                        <h3 className="text-xs font-bold text-[#848e9c] uppercase mb-3">AI Board of Advisors</h3>
                        <div className="space-y-2">
                            {/* XGBoost */}
                            <div className="flex justify-between items-center bg-[#2b3139]/30 p-2 rounded border border-[#2b3139]">
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-white">Quant Model</span>
                                    <span className="text-[9px] text-[#848e9c]">XGBoost v2</span>
                                </div>
                                <div className="text-right">
                                    <div className={`text-xs font-bold ${xgb.signal === 'Bullish' ? 'text-[#0ecb81]' : xgb.signal === 'Bearish' ? 'text-[#f6465d]' : 'text-white'}`}>
                                        {xgb.signal}
                                    </div>
                                    <div className="text-[9px] text-[#848e9c]">{xgb.probability}% Prob.</div>
                                </div>
                            </div>

                            {/* LSTM */}
                            <div className="flex justify-between items-center bg-[#2b3139]/30 p-2 rounded border border-[#2b3139]">
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-white">Pattern AI</span>
                                    <span className="text-[9px] text-[#848e9c]">LSTM Neural Net</span>
                                </div>
                                <div className="text-right">
                                    <div className={`text-xs font-bold ${lstm.signal === 'Bullish' ? 'text-[#0ecb81]' : lstm.signal === 'Bearish' ? 'text-[#f6465d]' : 'text-white'}`}>
                                        {lstm.signal}
                                    </div>
                                    <div className="text-[9px] text-[#848e9c]">{lstm.confidence}% Conf.</div>
                                </div>
                            </div>

                            {/* Sentiment */}
                            <div className="flex justify-between items-center bg-[#2b3139]/30 p-2 rounded border border-[#2b3139]">
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-white">News Sentiment</span>
                                    <span className="text-[9px] text-[#848e9c]">FinBERT NLP</span>
                                </div>
                                <div className="text-right">
                                    <div className={`text-xs font-bold ${sentimentExpert.score > 20 ? 'text-[#0ecb81]' : sentimentExpert.score < -20 ? 'text-[#f6465d]' : 'text-white'}`}>
                                        {sentimentExpert.label}
                                    </div>
                                    <div className="text-[9px] text-[#848e9c]">Score: {sentimentExpert.score}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* AI Select / Technicals */}
                    <div>
                        <h3 className="text-xs font-bold text-[#848e9c] uppercase mb-3">Technical Factors</h3>
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs">
                                <span className="text-[#848e9c]">RSI (14)</span>
                                <span className="text-white">{breakdown.rsi_val?.toFixed(1) || 50.0}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-[#848e9c]">Trend Strength</span>
                                <span className="text-white">{breakdown.trend_normalized?.toFixed(1) || 0.0}</span>
                            </div>
                             <div className="flex justify-between text-xs">
                                <span className="text-[#848e9c]">Sentiment</span>
                                <span className={current_sentiment > 0 ? 'text-[#0ecb81]' : 'text-[#f6465d]'}>
                                    {current_sentiment?.toFixed(2) || 0.00}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div className="mt-auto bg-gradient-to-b from-[#2b3139] to-[#1e2329] p-3 rounded border border-[#2b3139]">
                         <div className="flex items-center gap-2 mb-2">
                             <Shield className="w-4 h-4 text-[#0ecb81]" />
                             <span className="text-xs font-bold text-white">Risk Analysis</span>
                         </div>
                         <p className="text-[10px] text-[#848e9c] leading-relaxed">
                            Volatility is moderate. AI suggests maintaining current positions with a trailing stop-loss at ${support.toFixed(2)}.
                         </p>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default Dashboard;
