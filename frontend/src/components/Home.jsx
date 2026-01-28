import { TrendingUp, TrendingDown, ArrowRight, Loader2, BarChart2, Newspaper, Activity, Zap, RefreshCw } from 'lucide-react';
import { useState, useEffect } from 'react';
import logoDark from '../assets/logo-dark.png';
import logoLight from '../assets/logo-light.png';

// Internal TradingView Widget Component
const TradingViewWidget = () => {
    useEffect(() => {
        if (document.getElementById('tv-widget-script')) return;

        const script = document.createElement('script');
        script.id = 'tv-widget-script';
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js";
        script.async = true;
        script.innerHTML = JSON.stringify({
            "exchanges": [],
            "dataSource": "SPX500",
            "grouping": "sector",
            "blockSize": "market_cap_basic",
            "blockColor": "change",
            "locale": "en",
            "symbolUrl": "",
            "colorTheme": "dark",
            "hasTopBar": false,
            "isDataSetEnabled": false,
            "isZoomEnabled": true,
            "hasSymbolTooltip": true,
            "width": "100%",
            "height": "100%"
        });

        const container = document.getElementById('tradingview-container');
        if (container) container.appendChild(script);

        return () => {
            if (container) container.innerHTML = '';
        };
    }, []);

    return (
        <div className="tradingview-widget-container h-[500px] w-full rounded-2xl overflow-hidden border border-[var(--border-color)] shadow-lg">
            <div id="tradingview-container" className="tradingview-widget-container__widget h-full w-full"></div>
        </div>
    );
};

const MarketCard = ({ title, data, icon: Icon, type, onSearch }) => {
    return (
        <div className="card h-full flex flex-col hover:shadow-lg transition-shadow duration-300 overflow-hidden group">
            <div className="p-4 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-secondary)]/50">
                <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg ${
                        type === 'gainer' ? 'bg-green-500/10 text-green-500' : 
                        type === 'loser' ? 'bg-red-500/10 text-red-500' : 
                        'bg-blue-500/10 text-blue-500'
                    }`}>
                        {Icon && <Icon className="w-5 h-5" />}
                    </div>
                    <h3 className="font-bold text-sm uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>{title}</h3>
                </div>
            </div>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
                {data.length === 0 ? (
                     <div className="flex flex-col items-center justify-center h-32 text-gray-500 text-sm">
                        <span>No data available</span>
                     </div>
                ) : (
                    <table className="w-full">
                        <tbody className="divide-y divide-[var(--border-color)]">
                            {data.map((item, idx) => (
                                <tr 
                                    key={idx}
                                    onClick={() => onSearch(item.symbol)}
                                    className="cursor-pointer hover:bg-[var(--bg-secondary)] transition-colors group/row"
                                >
                                    <td className="py-3 px-2">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>{item.symbol}</span>
                                            <span className="text-[10px] truncate max-w-[80px]" style={{ color: 'var(--text-secondary)' }}>
                                                {item.name}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="text-right py-3 px-2">
                                        <div className="flex flex-col items-end">
                                            <span className="font-mono text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                                                {item.price}
                                            </span>
                                            {item.volume_fmt ? (
                                                <span className="text-[10px] text-gray-400 font-mono">Vol: {item.volume_fmt}</span>
                                            ) : (
                                                <span className={`text-xs font-bold ${item.change >= 0 ? 'text-[var(--color-up)]' : 'text-[var(--color-down)]'}`}>
                                                    {item.change >= 0 ? '+' : ''}{item.change}%
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

const Home = ({ onSearch, activeTab = 'markets', isDark }) => {
    const [movers, setMovers] = useState({ gainers: [], losers: [], active: [] });
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [visibleNewsCount, setVisibleNewsCount] = useState(12);
    const [newsLoading, setNewsLoading] = useState(false);

    const fetchNews = async (force = false) => {
        setNewsLoading(true);
        try {
            if (force) setNews([]); 
            const timestamp = new Date().getTime();
            const url = `http://127.0.0.1:5000/api/general-news?t=${timestamp}${force ? '&force=true' : ''}`;
            const resNews = await fetch(url);
            const dataNews = await resNews.json();
            if (Array.isArray(dataNews)) setNews(dataNews);
        } catch (err) { console.error("News Fetch Error", err); }
        setNewsLoading(false);
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Try cache first for immediate render
                const cachedMovers = localStorage.getItem('market_movers');
                const cachedTime = localStorage.getItem('market_movers_ts');
                if (cachedMovers && cachedTime && (Date.now() - parseInt(cachedTime)) < 1800000) {
                    setMovers(JSON.parse(cachedMovers));
                    setLoading(false); // Valid cache found
                }

                // Fetch fresh data in background if cache is old or missing
                if (!cachedMovers || (cachedTime && (Date.now() - parseInt(cachedTime)) >= 1800000)) {
                    const res = await fetch('http://127.0.0.1:5000/api/market-movers');
                    const data = await res.json();
                    if (data.gainers) {
                        setMovers(data);
                        localStorage.setItem('market_movers', JSON.stringify(data));
                        localStorage.setItem('market_movers_ts', Date.now().toString());
                    }
                }
            } catch (err) { console.error("Movers Fetch Error", err); }
            
            await fetchNews(false);

            setLoading(false);
        };

        fetchData();
    }, []);

    const handleLoadMore = () => setVisibleNewsCount(prev => prev + 6);

    const popularTickers = [
        { sym: 'AAPL', name: 'Apple' },
        { sym: 'MSFT', name: 'Microsoft' },
        { sym: 'GOOGL', name: 'Google' },
        { sym: 'AMZN', name: 'Amazon' }, 
        { sym: 'NVDA', name: 'Nvidia' }
    ];

    return (
        <div className="animate-fade-in pb-20">
            {/* HERO SECTION */}
            {activeTab === 'markets' && (
                <div className="relative overflow-hidden mb-8 rounded-3xl bg-gradient-to-r from-[var(--bg-card)] to-[var(--bg-secondary)] border border-[var(--border-color)] shadow-sm flex flex-col md:flex-row min-h-[350px]">
                    {/* Background Glow */}
                    <div className="absolute top-0 right-0 w-80 h-80 bg-[var(--accent-color)] opacity-5 rounded-full blur-3xl transform translate-x-1/3 -translate-y-1/3 pointer-events-none"></div>
                    
                    {/* Text Content (Left) */}
                    <div className="md:w-3/5 flex flex-col justify-center p-8 z-20">
                        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 leading-tight" style={{ color: 'var(--text-primary)' }}>
                            Refracting Data into <br/>
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent-color)] to-blue-600">
                                Clear Insight
                            </span>
                        </h1>
                        
                        <p className="text-base md:text-lg mb-6 leading-relaxed opacity-80 max-w-lg" style={{ color: 'var(--text-secondary)' }}>
                            Just as a prism unifies scattered light, our AI engine fuses complex market data and global news sentiment into a single, high-confidence trading signal.
                        </p>
                        
                        <div className="flex flex-wrap items-center gap-2">
                            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)] mr-2">The Big 5:</span>
                            {popularTickers.map((t) => (
                                <button
                                    key={t.sym}
                                    onClick={() => onSearch(t.sym)}
                                    className="px-3 py-1 rounded-full text-xs font-bold bg-[var(--bg-primary)] border border-[var(--border-color)] hover:border-[var(--accent-color)] hover:text-[var(--accent-color)] transition-all shadow-sm"
                                    style={{ color: 'var(--text-primary)' }}
                                >
                                    {t.sym}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Large Logo / Graphic (Right) */}
                    <div className="md:w-2/5 flex items-center justify-center relative p-4">
                         <div className="relative z-10 w-full h-full flex items-center justify-center">
                            <img 
                                src={isDark ? logoDark : logoLight} 
                                alt="Prism Finance" 
                                className="max-h-[250px] w-auto object-contain drop-shadow-xl"
                            />
                         </div>
                    </div>
                </div>
            )}

            {/* MARKETS TAB */}
            {activeTab === 'markets' && (
                <div className="max-w-7xl mx-auto space-y-12">
                    {/* Market Movers Grid */}
                    <div>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                                <Activity className="w-5 h-5 text-[var(--accent-color)]" /> 
                                Market Movers
                            </h2>
                            <span className="text-xs font-medium px-2 py-1 rounded bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-secondary)]">
                                Live Updates
                            </span>
                        </div>

                        {loading && !movers.gainers.length ? (
                            <div className="flex justify-center items-center h-64 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)]">
                                <Loader2 className="w-10 h-10 animate-spin text-[var(--accent-color)]" />
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <MarketCard title="Top Gainers" data={movers.gainers} icon={TrendingUp} type="gainer" onSearch={onSearch} />
                                <MarketCard title="Top Losers" data={movers.losers} icon={TrendingDown} type="loser" onSearch={onSearch} />
                                <MarketCard title="Most Active" data={movers.active || []} icon={Activity} type="active" onSearch={onSearch} />
                            </div>
                        )}
                    </div>

                    {/* Heatmap Section */}
                    <div>
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                            <BarChart2 className="w-5 h-5 text-[var(--accent-color)]" /> 
                            S&P 500 Heatmap
                        </h2>
                        <TradingViewWidget />
                        <div className="mt-3 flex justify-end">
                            <a href="https://www.tradingview.com/" target="_blank" rel="noopener noreferrer" className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent-color)] transition-colors">
                                Heatmap provided by TradingView
                            </a>
                        </div>
                    </div>
                </div>
            )}

            {/* NEWS TAB */}
            {activeTab === 'news' && (
                <div className="max-w-7xl mx-auto pt-4">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-3xl font-bold mb-2 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
                                Global Markets News
                            </h2>
                            <p className="text-[var(--text-secondary)]">Curated headlines from top financial sources.</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {news.length > 0 ? (
                            news.slice(0, visibleNewsCount).map((item, idx) => (
                                <a
                                    key={idx}
                                    href={item.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group flex flex-col h-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                                >
                                    <div className="h-48 overflow-hidden relative bg-gray-200 dark:bg-gray-800">
                                        <img
                                            src={item.image || "https://images.unsplash.com/photo-1611974765270-ca1258634369?q=80&w=500&auto=format&fit=crop"}
                                            alt={item.title}
                                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                            onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1611974765270-ca1258634369?q=80&w=500&auto=format&fit=crop"; }}
                                        />
                                        <div className="absolute top-3 right-3 bg-[var(--bg-primary)]/80 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-bold shadow-sm border border-[var(--border-color)]" style={{ color: 'var(--text-primary)' }}>
                                            {item.publisher}
                                        </div>
                                    </div>

                                    <div className="p-6 flex flex-col flex-1">
                                        <div className="text-xs font-medium mb-3" style={{ color: 'var(--text-secondary)' }}>
                                            {item.published}
                                        </div>

                                        <h3 className="text-lg font-bold leading-snug mb-4 group-hover:text-[var(--accent-color)] transition-colors line-clamp-3" style={{ color: 'var(--text-primary)' }}>
                                            {item.title}
                                        </h3>

                                        <div className="mt-auto pt-4 border-t border-[var(--border-color)] flex items-center text-sm font-semibold text-[var(--accent-color)] opacity-100 transition-all duration-300">
                                            Read Full Story
                                            <ArrowRight className="w-4 h-4 ml-2" />
                                        </div>
                                    </div>
                                </a>
                            ))
                        ) : (
                            <div className="col-span-3 py-32 text-center">
                                <Loader2 className="w-12 h-12 text-[var(--accent-color)] animate-spin mx-auto mb-4" />
                                <p className="text-lg font-medium" style={{ color: 'var(--text-secondary)' }}>Curating the latest headlines...</p>
                            </div>
                        )}
                    </div>

                    {news.length > visibleNewsCount && (
                        <div className="flex justify-center mt-16">
                            <button
                                onClick={handleLoadMore}
                                className="px-8 py-3 rounded-full font-bold text-sm bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-[var(--accent-color)] hover:text-[var(--accent-color)] transition-all shadow-sm"
                                style={{ color: 'var(--text-primary)' }}
                            >
                                Load More News
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Home;