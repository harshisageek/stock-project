import React, { useEffect, useState } from 'react';
import { ArrowUpRight, ArrowDownRight, Activity, Search } from 'lucide-react';
import SearchBar from './SearchBar';

const AnalysisLanding = ({ onSearch }) => {
    const [trending, setTrending] = useState([]);

    useEffect(() => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000); 

        fetch('http://127.0.0.1:5000/api/market-movers', { signal: controller.signal })
            .then(res => res.json())
            .then(data => {
                clearTimeout(timeoutId);
                if (data.active) {
                    setTrending(data.active.slice(0, 4));
                }
            })
            .catch(err => {
                if (err.name !== 'AbortError') console.error(err);
            });
            
        return () => clearTimeout(timeoutId);
    }, []);

    const quickTickers = ["NVDA", "TSLA", "BTC-USD", "AAPL", "AMD"];

    return (
        <div className="min-h-[85vh] w-full flex flex-col items-center pt-20 pb-12 px-4 animate-fade-in">
            
            {/* 1. Main Content Container (Centered & Spaced) */}
            <div className="w-full max-w-3xl flex flex-col items-center space-y-12">
                
                {/* Brand / Hero */}
                <div className="text-center space-y-6">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[var(--bg-card)] shadow-lg mb-4 border border-[var(--border-color)]">
                        <Search className="w-8 h-8 text-[var(--accent-color)]" />
                    </div>
                    
                    <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-[var(--text-primary)]">
                        Deep Dive
                    </h1>
                    
                    <p className="text-xl text-[var(--text-secondary)] max-w-xl mx-auto font-light">
                        Comprehensive market intelligence powered by neural networks and sentiment analysis.
                    </p>
                </div>

                {/* Search Section */}
                <div className="w-full max-w-2xl space-y-6">
                    <div className="bg-[var(--bg-card)] rounded-2xl shadow-xl border border-[var(--border-color)] transition-shadow hover:shadow-2xl overflow-hidden">
                         <SearchBar onSearch={onSearch} autoFocus={true} placeholder="Search ticker symbol..." clean={true} />
                    </div>
                </div>

            </div>

            {/* 2. Market Pulse Section (Separated & Clean) */}
            {trending.length > 0 && (
                <div className="w-full max-w-5xl mt-24">
                    <div className="flex items-center gap-3 mb-8 px-2 border-b border-[var(--border-color)] pb-4">
                        <div className="p-2 rounded-lg bg-[var(--accent-color)]/10">
                            <Activity className="w-5 h-5 text-[var(--accent-color)]" />
                        </div>
                        <h2 className="text-lg font-bold text-[var(--text-primary)] uppercase tracking-wide">
                            Active Markets
                        </h2>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {trending.map((item, idx) => (
                            <div 
                                key={idx}
                                onClick={() => onSearch(item.symbol)}
                                className="group cursor-pointer bg-[var(--bg-card)] p-5 rounded-xl border border-[var(--border-color)] hover:border-[var(--accent-color)] hover:shadow-lg transition-all duration-300 relative overflow-hidden"
                            >
                                {/* Hover Gradient bg */}
                                <div className="absolute inset-0 bg-[var(--accent-color)]/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                
                                <div className="relative z-10">
                                    <div className="flex justify-between items-start mb-3">
                                        <span className="text-xl font-bold text-[var(--text-primary)] group-hover:text-[var(--accent-color)] transition-colors">
                                            {item.symbol}
                                        </span>
                                        <span className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${
                                            item.change >= 0 
                                            ? 'bg-green-500/10 text-green-600 dark:text-green-400' 
                                            : 'bg-red-500/10 text-red-600 dark:text-red-400'
                                        }`}>
                                            {item.change >= 0 ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                                            {Math.abs(item.change)}%
                                        </span>
                                    </div>
                                    
                                    <div className="flex justify-between items-end">
                                        <span className="text-sm font-medium text-[var(--text-secondary)] opacity-80 truncate max-w-[120px]">
                                            {item.name}
                                        </span>
                                        <span className="font-mono text-sm font-semibold text-[var(--text-primary)]">
                                            {item.price}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

        </div>
    );
};

export default AnalysisLanding;