import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import AnalysisLanding from './components/AnalysisLanding';
import WatchlistPage from './components/WatchlistPage';
import ErrorBoundary from './components/ErrorBoundary';

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
    <div className="h-screen flex flex-col bg-[#161a1e] text-[#eaecef] font-sans overflow-hidden">
        
        {/* Navigation */}
        <Navbar 
            toggleTheme={toggleTheme} 
            isDark={isDark} 
            onSearch={handleSearch} 
            activeTab={activeTab}
            onTabChange={handleTabChange}
        />

        {/* Main Content */}
        <main className={`flex-1 overflow-y-auto ${view === 'dashboard' ? 'p-0' : 'max-w-7xl mx-auto px-4 py-8 w-full'}`}>
            
            {/* Error Banner */}
            {error && (
                <div className="bg-[#f6465d]/20 border border-[#f6465d] text-[#f6465d] px-4 py-2 text-sm text-center">
                    <span className="font-bold">Error: </span>
                    <span>{error}</span>
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
                        <div className="flex flex-col items-center justify-center h-full w-full">
                            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#f0b90b] mb-4"></div>
                            <h2 className="text-lg font-mono text-[#848e9c]">
                                Processing Market Data: {ticker}...
                            </h2>
                        </div>
                    ) : (
                        stockData ? (
                            <div className="h-full">
                                <ErrorBoundary>
                                    <Dashboard 
                                        data={stockData} 
                                        ticker={ticker} 
                                        onRangeChange={handleRangeChange} 
                                        onRefresh={handleRefresh}
                                        isLoading={loading} 
                                    />
                                </ErrorBoundary>
                            </div>
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
