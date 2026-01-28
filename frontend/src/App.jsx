import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import AnalysisLanding from './components/AnalysisLanding';
import WatchlistPage from './components/WatchlistPage';

const API_URL = 'http://127.0.0.1:5000';

function App() {
  const [ticker, setTicker] = useState('');
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [view, setView] = useState('home'); // 'home' | 'dashboard'
  const [activeTab, setActiveTab] = useState('markets'); // 'markets' | 'news'

  // Dark Mode State
  const [isDark, setIsDark] = useState(true);

  // Apply Dark Mode to HTML tag
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  /* Reusable fetch function */
  const fetchStockData = async (tickerSymbol, range = '1W', force = false, companyName = null) => {
    if (!tickerSymbol) return;

    setLoading(true);
    // Switch to dashboard view and analysis tab on search
    setView('dashboard');
    setActiveTab('analysis');
    
    // Clear data only if it's a fresh search
    if (range === '1W' && !force && tickerSymbol !== ticker) {
        setStockData(null);
    }
    
    setTicker(tickerSymbol);
    setError('');

    try {
      const url = `${API_URL}/api/analyze?ticker=${tickerSymbol}&range=${range}&force=${force}&name=${encodeURIComponent(companyName || '')}`;
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

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setStockData(data);
      }
    } catch (err) {
      console.error("Fetch Error:", err);
      setError(err.message || "Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (tickerInput, name) => {
    if (!tickerInput) return;
    fetchStockData(tickerInput, '1W', false, name);
  };

  const handleRangeChange = (newRange) => {
    fetchStockData(ticker, newRange);
  };

  const handleRefresh = () => {
      fetchStockData(ticker, '1W', true);
  };

  // Define handler explicitly
  const handleTabChange = (tab) => {
      console.log("Tab Changed:", tab);
      if (tab === 'analysis') {
          setView('dashboard');
      } else if (tab === 'watchlist') {
          setView('watchlist');
      } else {
          setView('home');
      }
      setActiveTab(tab);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-secondary)] text-[var(--text-primary)] font-sans transition-colors duration-200">
        
        {/* Navigation */}
        <Navbar 
            toggleTheme={toggleTheme} 
            isDark={isDark} 
            onSearch={handleSearch} 
            activeTab={activeTab}
            onTabChange={handleTabChange}
        />

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            
            {/* Error Banner */}
            {error && (
                <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            )}

            {/* Views */}
            {view === 'home' && (
                <Home onSearch={handleSearch} activeTab={activeTab} isDark={isDark} />
            )}

            {view === 'watchlist' && (
                <WatchlistPage onSearch={handleSearch} />
            )}

            {view === 'dashboard' && (
                <>
                    {!stockData && loading ? (
                        <div className="flex flex-col items-center justify-center min-h-[70vh] w-full">
                            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-[var(--accent-color)] mb-6"></div>
                            <h2 className="text-xl font-bold animate-pulse tracking-wide" style={{ color: 'var(--text-primary)' }}>
                                Analyzing Market Data for {ticker}...
                            </h2>
                        </div>
                    ) : (
                        stockData ? (
                            <Dashboard 
                                data={stockData} 
                                ticker={ticker} 
                                onRangeChange={handleRangeChange} 
                                onRefresh={handleRefresh}
                                isLoading={loading} 
                            />
                        ) : (
                            <AnalysisLanding onSearch={handleSearch} />
                        )
                    )}
                </>
            )}
        </main>
    </div>
  );
}

export default App;
