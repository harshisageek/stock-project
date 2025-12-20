/**
 * Stock Sentiment Analyzer - Main App Component
 * 
 * Complete Rewrite: Clean, Spacious, Centered Layout.
 */

import { useState } from 'react';
import Dashboard from './components/Dashboard';
import DemoModeBanner from './components/DemoModeBanner';
import SearchBar from './components/SearchBar';
import { Loader2, Search } from 'lucide-react';

const API_URL = 'http://127.0.0.1:5000';

function App() {
  const [ticker, setTicker] = useState('');
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState('');

  /* Reusable fetch function */
  const fetchStockData = async (tickerSymbol, range = '1W') => {
    if (!tickerSymbol) return;

    setLoading(true);
    // Only reset states if it's a new search, not a range update
    if (range === '1W') {
      setDemoMode(false);
      setError('');
      setStockData(null);
      setHasSearched(true);
    }

    try {
      const response = await fetch(`${API_URL}/api/analyze?ticker=${tickerSymbol}&range=${range}`);
      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setStockData(data);
        if (data.circuit_breaker) {
          setDemoMode(true);
        }
      }
    } catch (err) {
      console.error(err);
      setError("Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (tickerInput) => {
    // If called from event (form submit), ignore or handle differently?
    // references to this function in App.jsx are now only from SearchBar which passes a string.
    // However, if there are any legacy calls, we should be careful. 
    // But since we are replacing all UI, we can assume tickerInput is the string.

    if (!tickerInput) return;
    setTicker(tickerInput); // Sync state

    // Reset specific states for new search
    setStockData(null);
    setHasSearched(true);
    setDemoMode(false);
    setError('');

    fetchStockData(tickerInput, '1W');
  };

  const handleRangeChange = (newRange) => {
    fetchStockData(ticker, newRange);
  };

  // 1. LANDING STATE (Initial)
  if (!hasSearched) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-[#1a103c] overflow-hidden">

        {/* Main Glass Card */}
        <div className="relative z-10 w-full max-w-md p-8 glass-panel transform transition-all duration-500">

          <div className="text-center mb-10">
            <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 drop-shadow-lg mb-4">
              AI Stock Sentiment
            </h1>
            <p className="text-gray-200 text-lg">
              Analyze market sentiment instantly using sophisticated AI models.
            </p>
          </div>

          <SearchBar onSearch={handleSearch} isLoading={loading} />

        </div>
      </div>
    );
  }

  // 2. LOADING STATE
  if (loading && !stockData) { // Only show full loader if no data exists (initial search)
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 text-white font-sans flex flex-col items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl rounded-3xl p-12 max-w-lg w-full text-center">
          <Loader2 className="w-16 h-16 text-purple-400 animate-spin mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
            Scanning Market Data...
          </h2>
          <p className="text-gray-300">Analyzing thousands of news points for {ticker}</p>
        </div>
      </div>
    );
  }

  // 3. DASHBOARD STATE
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 text-white font-sans overflow-x-hidden">

      {/* Circuit Breaker Banner */}
      {demoMode && <DemoModeBanner />}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Header / Search Bar Compact */}
        <header className="flex flex-col md:flex-row items-center justify-between mb-10 gap-4">
          <div
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setHasSearched(false)}
          >
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-lg group-hover:shadow-purple-500/50 transition-all">
              <Search className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-100">AI Stock Sentiment</h1>
          </div>

          <SearchBar onSearch={handleSearch} isLoading={loading} inline={true} />
        </header>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-100 p-4 rounded-xl mb-8 text-center max-w-2xl mx-auto backdrop-blur-sm">
            {error}
          </div>
        )}

        {/* Dashboard Content */}
        {stockData && !error && (
          <Dashboard
            data={stockData}
            ticker={ticker}
            onRangeChange={handleRangeChange}
            isLoading={loading}
          />
        )}

      </div>
    </div>
  );
}

export default App;
