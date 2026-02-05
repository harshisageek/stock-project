import React, { useEffect, useState } from 'react';
import { Star, Trash2, Plus, ArrowRight, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getWatchlist, removeFromWatchlist, addToWatchlist } from '../supabase';
import AuthModal from './AuthModal';
import SearchBar from './SearchBar';

const WatchlistPage = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [watchlist, setWatchlist] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showAuth, setShowAuth] = useState(false);
    
    // Quick Add State
    const [quickAdd, setQuickAdd] = useState('');
    const [adding, setAdding] = useState(false);

    useEffect(() => {
        if (user) {
            fetchWatchlist();
        } else {
            setWatchlist([]);
        }
    }, [user]);

    const fetchWatchlist = async () => {
        setLoading(true);
        const { data } = await getWatchlist(user.id);
        if (data) setWatchlist(data);
        setLoading(false);
    };

    const handleRemove = async (e, ticker) => {
        e.stopPropagation(); // Prevent card click
        if (!confirm(`Remove ${ticker} from watchlist?`)) return;
        
        const { error } = await removeFromWatchlist(user.id, ticker);
        if (!error) {
            setWatchlist(prev => prev.filter(item => item.ticker !== ticker));
        }
    };
    
    const handleQuickAdd = async (e) => {
        e.preventDefault();
        if (!quickAdd.trim()) return;
        
        setAdding(true);
        const ticker = quickAdd.trim().toUpperCase();
        // Check if already exists
        if (watchlist.find(i => i.ticker === ticker)) {
            setQuickAdd('');
            setAdding(false);
            return;
        }

        const { data, error } = await addToWatchlist(user.id, ticker);
        if (!error) {
            fetchWatchlist();
            setQuickAdd('');
        }
        setAdding(false);
    };

    // --- GUEST VIEW ---
    if (!user) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4 animate-in fade-in zoom-in duration-500">
                <div className="p-6 rounded-full mb-8 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                    <Lock className="w-12 h-12 text-gray-400" />
                </div>
                <h1 className="text-3xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                    Your Watchlist is Locked
                </h1>
                <p className="text-lg mb-8 max-w-md" style={{ color: 'var(--text-secondary)' }}>
                    Sign in to track your favorite stocks, monitor sentiment, and build your portfolio.
                </p>
                <div className="flex gap-4">
                    <button 
                        onClick={() => setShowAuth(true)}
                        className="px-8 py-3 rounded-full font-bold text-[#181a20] transition-transform active:scale-95"
                        style={{ backgroundColor: 'var(--accent-color)' }}
                    >
                        Sign In / Sign Up
                    </button>
                </div>
                <AuthModal isOpen={showAuth} onClose={() => setShowAuth(false)} />
            </div>
        );
    }

    // --- USER VIEW ---
    return (
        <div className="max-w-7xl mx-auto px-4 py-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
                        <Star className="w-8 h-8 fill-[var(--accent-color)] text-[var(--accent-color)]" />
                        My Watchlist
                    </h1>
                    <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                        {watchlist.length} stocks tracked
                    </p>
                </div>

                {/* Quick Add Form */}
                <form onSubmit={handleQuickAdd} className="flex gap-2 w-full md:w-auto">
                    <input 
                        type="text" 
                        placeholder="Add Ticker (e.g. NVDA)..."
                        value={quickAdd}
                        onChange={(e) => setQuickAdd(e.target.value)}
                        className="px-4 py-2 rounded-lg bg-[var(--bg-secondary)] border border-[var(--border-color)] outline-none focus:border-[var(--accent-color)] transition-colors w-full md:w-64"
                        style={{ color: 'var(--text-primary)' }}
                    />
                    <button 
                        type="submit"
                        disabled={adding || !quickAdd}
                        className="p-2 rounded-lg bg-[var(--accent-color)] text-black hover:opacity-90 disabled:opacity-50"
                    >
                        <Plus className="w-5 h-5" />
                    </button>
                </form>
            </div>

            {/* Grid */}
            {watchlist.length === 0 ? (
                <div className="text-center py-20 border-2 border-dashed rounded-2xl" style={{ borderColor: 'var(--border-color)' }}>
                    <p className="text-gray-500 mb-4">Your watchlist is empty.</p>
                    <p className="text-sm text-gray-400">Use the box above to add stocks.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {watchlist.map((item) => (
                        <div 
                            key={item.id}
                            onClick={() => navigate(`/analysis/${item.ticker}`)}
                            className="group relative p-6 rounded-xl border cursor-pointer hover:-translate-y-1 transition-all duration-300"
                            style={{ 
                                backgroundColor: 'var(--bg-card)', 
                                borderColor: 'var(--border-color)' 
                            }}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-[var(--bg-secondary)] flex items-center justify-center font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
                                        {item.ticker[0]}
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl" style={{ color: 'var(--text-primary)' }}>{item.ticker}</h3>
                                        <span className="text-xs text-[var(--accent-color)] uppercase tracking-wider">Tracked</span>
                                    </div>
                                </div>
                                <button 
                                    onClick={(e) => handleRemove(e, item.ticker)}
                                    className="p-2 rounded-full hover:bg-red-500/10 text-gray-400 hover:text-red-500 transition-colors z-10"
                                    title="Remove from watchlist"
                                >
                                    <Star className="w-5 h-5 fill-current" />
                                </button>
                            </div>
                            
                            <div className="flex items-center justify-between mt-4 pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                                <span className="text-sm text-[var(--text-secondary)]">Click to analyze sentiment</span>
                                <ArrowRight className="w-4 h-4 text-[var(--text-secondary)] group-hover:text-[var(--accent-color)] transition-colors" />
                            </div>

                            {/* Hover Border Glow */}
                            <div className="absolute inset-0 rounded-xl border-2 border-[var(--accent-color)] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default WatchlistPage;
