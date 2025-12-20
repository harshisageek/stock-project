/**
 * SearchBar Component
 * 
 * Glassmorphism search input with Analyze button
 */

import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

const API_URL = 'http://127.0.0.1:5000';

function SearchBar({ onSearch, isLoading, inline = false }) {
    const [ticker, setTicker] = useState('');
    const [results, setResults] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [searchLoading, setSearchLoading] = useState(false);

    // Debounce logic
    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (ticker.trim().length > 1) {
                setSearchLoading(true);
                try {
                    const response = await fetch(`${API_URL}/api/search?q=${ticker}`);
                    const data = await response.json();
                    setResults(data.data || []);
                    setShowDropdown(true);
                } catch (error) {
                    console.error("Search failed:", error);
                    setResults([]);
                } finally {
                    setSearchLoading(false);
                }
            } else {
                setResults([]);
                setShowDropdown(false);
            }
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [ticker]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (ticker.trim() && !isLoading) {
            onSearch(ticker.trim().toUpperCase());
            setShowDropdown(false);
        }
    };

    const handleSelect = (symbol) => {
        setTicker(symbol);
        onSearch(symbol);
        setShowDropdown(false);
    };

    // Close dropdown when clicking outside (simple implementation: blur with delay)
    const handleBlur = () => {
        setTimeout(() => setShowDropdown(false), 200);
    };

    if (inline) {
        // Inline version for dashboard header
        return (
            <div className="relative z-50">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <div className="relative">
                        <Search
                            size={18}
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none"
                            style={{ color: 'var(--text-secondary)' }}
                        />
                        <input
                            type="text"
                            value={ticker}
                            onChange={(e) => setTicker(e.target.value)}
                            onFocus={() => ticker.length > 1 && setShowDropdown(true)}
                            onBlur={handleBlur}
                            placeholder="Enter ticker..."
                            disabled={isLoading}
                            className="pl-10 pr-4 py-2 rounded-lg border text-sm w-48 focus:outline-none focus:ring-1 focus:ring-purple-500"
                            style={{
                                background: 'rgba(20, 20, 40, 0.8)',
                                borderColor: 'var(--glass-border)',
                                color: 'var(--text-primary)',
                            }}
                        />
                        {/* Autocomplete Dropdown - Inline */}
                        {showDropdown && results.length > 0 && (
                            <div className="absolute top-full left-0 mt-2 w-64 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar">
                                {results.map((item) => (
                                    <div
                                        key={item.symbol}
                                        className="px-4 py-3 hover:bg-white/10 cursor-pointer transition-colors border-b border-white/5 last:border-none"
                                        onMouseDown={() => handleSelect(item.symbol)}
                                    >
                                        <div className="flex justify-between items-center">
                                            <span className="font-bold text-white">{item.symbol}</span>
                                            <span className="text-xs text-gray-400">{item.instrument_name}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    <button
                        type="submit"
                        disabled={isLoading || !ticker.trim()}
                        className="btn-primary px-4 py-2 rounded-lg font-medium text-white text-sm bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90 transition-opacity"
                    >
                        Analyze
                    </button>
                </form>
            </div>
        );
    }

    // Landing page version (centered, larger)
    return (
        <div className="glass-card p-8 w-full max-w-lg neon-glow-cyan relative z-50">
            <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4 relative">
                {/* Search input */}
                <div className="relative w-full">
                    <Search
                        size={20}
                        className="absolute left-4 top-1/2 transform -translate-y-1/2 pointer-events-none"
                        style={{ color: 'var(--text-secondary)' }}
                    />
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value)}
                        onFocus={() => ticker.length > 1 && setShowDropdown(true)}
                        onBlur={handleBlur}
                        placeholder="Enter stock ticker (e.g., AAPL)"
                        disabled={isLoading}
                        className="w-full pl-12 pr-4 py-4 rounded-xl border text-base focus:outline-none focus:ring-2 focus:ring-purple-500 bg-black/30 text-white placeholder-gray-400"
                        style={{
                            borderColor: 'var(--glass-border)',
                        }}
                    />

                    {/* Autocomplete Dropdown - Landing */}
                    {showDropdown && results.length > 0 && (
                        <div className="absolute top-full left-0 mt-2 w-full bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar z-50">
                            {results.map((item) => (
                                <div
                                    key={item.symbol}
                                    className="px-6 py-4 hover:bg-white/10 cursor-pointer transition-colors border-b border-white/5 last:border-none"
                                    onMouseDown={() => handleSelect(item.symbol)}
                                >
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <span className="font-bold text-white text-lg block">{item.symbol}</span>
                                            <span className="text-sm text-gray-400">{item.instrument_name}</span>
                                        </div>
                                        <span className="text-xs px-2 py-1 bg-white/10 rounded text-gray-300">{item.exchange}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Analyze button */}
                <button
                    type="submit"
                    disabled={isLoading || !ticker.trim()}
                    className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-bold text-lg text-white shadow-lg hover:opacity-90 hover:scale-[1.02] transition-all transform active:scale-95"
                >
                    Analyze Market Data
                </button>
            </form>
        </div>
    );
}

export default SearchBar;
