import { Moon, Sun, Menu, X, LogOut, LayoutDashboard, Newspaper, Eye, Search, BarChart3 } from 'lucide-react';
import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';
import { useAuth } from '../context/AuthContext';
import AuthModal from './AuthModal';
import logoDark from '../assets/logo-dark.png';
import logoLight from '../assets/logo-light.png';

const Navbar = ({ toggleTheme, isDark }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const { user, signOut } = useAuth();
    const navigate = useNavigate();
    
    // Custom Tab Component for Desktop
    const NavTab = ({ label, to, icon: Icon }) => {
        return (
            <NavLink 
                to={to}
                className={({ isActive }) => `group flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive 
                    ? 'bg-[var(--accent-color)] text-[#181a20] shadow-md transform scale-105' 
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] hover:text-[var(--text-primary)]'
                }`}
            >
                <Icon className="w-4 h-4 group-hover:stroke-[2.5px]" />
                <span>{label}</span>
            </NavLink>
        );
    };

    return (
        <nav className="sticky top-0 z-50 border-b backdrop-blur-md transition-all duration-200"
            style={{ 
                backgroundColor: 'rgba(var(--bg-card-rgb), 0.8)', 
                background: isDark ? '#1e2329' : 'rgba(255, 255, 255, 0.95)',
                borderColor: '#2b3139' 
            }}
        >
            <div className="w-full px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16 py-2">
                    
                    {/* Left: Brand & Logo */}
                    <Link to="/" className="flex-shrink-0 flex items-center gap-3 cursor-pointer group">
                        <div className="w-10 h-10 flex items-center justify-center transition-transform group-hover:scale-105">
                            <img 
                                src={isDark ? logoDark : logoLight} 
                                alt="Prism Logo" 
                                className="w-full h-full object-contain"
                            />
                        </div>
                        <div className="flex flex-col justify-center">
                            <span className="font-bold text-xl tracking-tight" style={{ color: 'var(--text-primary)' }}>
                                PRISM
                            </span>
                        </div>
                    </Link>

                    {/* Center: Navigation Tabs (Desktop) */}
                    <div className="hidden md:flex items-center gap-1 bg-[var(--bg-secondary)] p-1.5 rounded-xl border border-[var(--border-color)]">
                        <NavTab label="Markets" to="/" icon={BarChart3} />
                        <NavTab label="News" to="/news" icon={Newspaper} />
                        <NavTab label="Watchlist" to="/watchlist" icon={Eye} />
                        
                        {/* Vertical Divider */}
                        <div className="w-px h-5 bg-[var(--border-color)] mx-1"></div>
                        
                        <NavTab label="DeepDive" to="/analysis" icon={Search} />
                    </div>

                    {/* Right: Search & Actions */}
                    <div className="flex items-center gap-3 lg:gap-5">
                        
                        {/* Search Bar - Collapses on smaller md screens */}
                        <div className="hidden lg:block w-64">
                            <SearchBar inline={true} />
                        </div>

                        {/* Theme Toggle */}
                        <button 
                            type="button"
                            onClick={toggleTheme}
                            className="p-2.5 rounded-lg hover:bg-[var(--bg-secondary)] border border-transparent hover:border-[var(--border-color)] transition-all"
                            style={{ color: 'var(--text-secondary)' }}
                            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
                        >
                            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                        </button>
                        
                        {/* User Actions */}
                        <div className="hidden md:flex items-center">
                            {user ? (
                                <div className="flex items-center gap-3 pl-3 border-l border-[var(--border-color)]">
                                    <span className="text-sm font-medium hidden lg:block" style={{ color: 'var(--text-primary)' }}>
                                        {user.email.split('@')[0]}
                                    </span>
                                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-[var(--bg-secondary)] to-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-center text-[var(--text-primary)] font-bold shadow-sm">
                                        {user.email[0].toUpperCase()}
                                    </div>
                                    <button 
                                        onClick={signOut}
                                        className="p-2 rounded-lg hover:bg-red-500/10 hover:text-red-500 transition-colors"
                                        title="Sign Out"
                                        style={{ color: 'var(--text-secondary)' }}
                                    >
                                        <LogOut className="w-4 h-4" />
                                    </button>
                                </div>
                            ) : (
                                <div className="flex gap-3 pl-2">
                                    <button 
                                        onClick={() => setShowAuthModal(true)}
                                        className="text-sm font-semibold hover:text-[var(--accent-color)] transition-colors" 
                                        style={{ color: 'var(--text-secondary)' }}
                                    >
                                        Log In
                                    </button>
                                    <button 
                                        onClick={() => setShowAuthModal(true)}
                                        className={`text-sm font-bold px-5 py-2 rounded-lg shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all ${
                                            isDark 
                                            ? 'bg-[#fcd535] text-black hover:bg-[#ffe066]' 
                                            : 'bg-blue-600 text-white hover:bg-blue-700'
                                        }`}
                                    >
                                        Get Started
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Mobile Menu Toggle */}
                        <button 
                            className="md:hidden p-2 rounded-lg hover:bg-[var(--bg-secondary)]"
                            onClick={() => setIsOpen(!isOpen)} 
                            style={{ color: 'var(--text-primary)' }}
                        >
                            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Auth Modal */}
            <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />

            {/* Mobile Menu Overlay */}
            {isOpen && (
                <div className="md:hidden border-t border-[var(--border-color)] animate-slide-down absolute w-full shadow-2xl" 
                    style={{ backgroundColor: 'var(--bg-card)' }}
                >
                    <div className="p-4 space-y-4">
                        <SearchBar inline={true} />
                        
                        <div className="grid grid-cols-2 gap-3">
                            <NavLink to="/" onClick={() => setIsOpen(false)} className={({isActive}) => `flex items-center justify-center gap-2 p-3 rounded-xl text-sm font-bold border transition-all ${isActive ? 'bg-[var(--accent-color)] border-[var(--accent-color)] text-black' : 'bg-[var(--bg-secondary)] border-transparent text-[var(--text-secondary)]'}`}>
                                <BarChart3 className="w-4 h-4" /> Markets
                            </NavLink>
                            <NavLink to="/news" onClick={() => setIsOpen(false)} className={({isActive}) => `flex items-center justify-center gap-2 p-3 rounded-xl text-sm font-bold border transition-all ${isActive ? 'bg-[var(--accent-color)] border-[var(--accent-color)] text-black' : 'bg-[var(--bg-secondary)] border-transparent text-[var(--text-secondary)]'}`}>
                                <Newspaper className="w-4 h-4" /> News
                            </NavLink>
                            <NavLink to="/watchlist" onClick={() => setIsOpen(false)} className={({isActive}) => `flex items-center justify-center gap-2 p-3 rounded-xl text-sm font-bold border transition-all ${isActive ? 'bg-[var(--accent-color)] border-[var(--accent-color)] text-black' : 'bg-[var(--bg-secondary)] border-transparent text-[var(--text-secondary)]'}`}>
                                <Eye className="w-4 h-4" /> Watchlist
                            </NavLink>
                            <NavLink to="/analysis" onClick={() => setIsOpen(false)} className={({isActive}) => `flex items-center justify-center gap-2 p-3 rounded-xl text-sm font-bold border transition-all ${isActive ? 'bg-[var(--accent-color)] border-[var(--accent-color)] text-black' : 'bg-[var(--bg-secondary)] border-transparent text-[var(--text-secondary)]'}`}>
                                <Search className="w-4 h-4" /> DeepDive
                            </NavLink>
                        </div>

                        {!user && (
                            <button 
                                onClick={() => { setShowAuthModal(true); setIsOpen(false); }}
                                className={`w-full py-3 rounded-xl font-bold text-center ${
                                    isDark ? 'bg-[#fcd535] text-black' : 'bg-blue-600 text-white'
                                }`}
                            >
                                Sign Up / Log In
                            </button>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;