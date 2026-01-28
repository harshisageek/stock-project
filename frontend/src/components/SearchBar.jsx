/**
 * SearchBar Component
 * 
 * Glassmorphism search input with Analyze button
 */

import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

const API_URL = 'http://127.0.0.1:5000';

function SearchBar({ onSearch, isLoading, inline = false, clean = false, placeholder, autoFocus }) {
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
            const match = results.find(r => r.symbol === ticker.trim().toUpperCase());
            const name = match ? match.instrument_name : null;
            onSearch(ticker.trim().toUpperCase(), name);
            setShowDropdown(false);
        }
    };

    const handleSelect = (symbol, name) => {
        setTicker(symbol);
        onSearch(symbol, name);
        setShowDropdown(false);
    };

    const handleBlur = () => {
        setTimeout(() => setShowDropdown(false), 200);
    };

    // 1. Inline Header Version
    if (inline) {
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
                            className="pl-10 pr-4 py-2 rounded-lg border text-sm w-48 focus:outline-none focus:ring-1 focus:ring-purple-500 transition-all"
                            style={{
                                background: 'var(--bg-card)',
                                borderColor: 'var(--border-color)',
                                color: 'var(--text-primary)',
                            }}
                        />
                        {showDropdown && results.length > 0 && (
                            <div className="absolute top-full left-0 mt-2 w-64 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar">
                                {results.map((item) => (
                                    <div
                                        key={item.symbol}
                                        className="px-4 py-3 hover:bg-[var(--bg-secondary)] cursor-pointer transition-colors border-b border-[var(--border-color)] last:border-none"
                                        onMouseDown={() => handleSelect(item.symbol)}
                                    >
                                        <div className="flex justify-between items-center">
                                            <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{item.symbol}</span>
                                            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{item.instrument_name}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    <button
                        type="submit"
                        disabled={isLoading || !ticker.trim()}
                        className="px-4 py-2 rounded-lg font-medium text-sm hover:opacity-90 transition-opacity"
                        style={{ backgroundColor: 'var(--accent-color)', color: '#181a20' }}
                    >
                        Analyze
                    </button>
                </form>
            </div>
        );
    }

    // 2. Landing Page Version (Clean or Card)
    return (
        <div className={`w-full relative z-50 ${clean ? '' : 'glass-card p-8 neon-glow-cyan'}`}>
            <form onSubmit={handleSubmit} className="flex items-center w-full relative">
                
                <Search
                    size={24}
                    className="absolute left-5 top-1/2 transform -translate-y-1/2 pointer-events-none z-10"
                    style={{ color: 'var(--text-secondary)' }}
                />
                
                <input
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    onFocus={() => ticker.length > 1 && setShowDropdown(true)}
                    onBlur={handleBlur}
                    autoFocus={autoFocus}
                    placeholder={placeholder || "Enter stock ticker (e.g., AAPL)"}
                    disabled={isLoading}
                    className="w-full pl-14 pr-4 py-5 rounded-2xl border text-lg font-medium focus:outline-none focus:border-[var(--accent-color)] focus:ring-1 focus:ring-[var(--accent-color)]/20 transition-all placeholder:text-gray-400"
                    style={{
                        backgroundColor: clean ? 'transparent' : 'rgba(0,0,0,0.3)',
                        borderColor: clean ? 'transparent' : 'var(--glass-border)',
                        color: 'var(--text-primary)',
                    }}
                />

                {/* Autocomplete Dropdown - Large */}
                {showDropdown && results.length > 0 && (
                    <div className="absolute top-full left-0 mt-4 w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar z-50">
                        {results.map((item) => (
                            <div
                                key={item.symbol}
                                className="px-6 py-4 hover:bg-[var(--bg-secondary)] cursor-pointer transition-colors border-b border-[var(--border-color)] last:border-none"
                                onMouseDown={() => handleSelect(item.symbol)}
                            >
                                <div className="flex justify-between items-center">
                                    <div>
                                        <span className="font-bold text-lg block" style={{ color: 'var(--text-primary)' }}>{item.symbol}</span>
                                        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{item.instrument_name}</span>
                                    </div>
                                    <span className="text-xs px-2 py-1 rounded border border-[var(--border-color)]" style={{ color: 'var(--text-secondary)' }}>{item.exchange}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </form>
        </div>
    );
}

export default SearchBar;