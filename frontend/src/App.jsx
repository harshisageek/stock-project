import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import AnalysisLanding from './components/AnalysisLanding';
import WatchlistPage from './components/WatchlistPage';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
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

  return (
    <div className="h-screen flex flex-col bg-[#161a1e] text-[#eaecef] font-sans overflow-hidden">
        
        {/* Navigation */}
        <Navbar 
            toggleTheme={toggleTheme} 
            isDark={isDark} 
        />

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
            <Routes>
                <Route path="/" element={<Home activeTab="markets" isDark={isDark} />} />
                <Route path="/news" element={<Home activeTab="news" isDark={isDark} />} />
                <Route path="/watchlist" element={<WatchlistPage />} />
                <Route path="/analysis" element={<AnalysisLanding />} />
                <Route 
                    path="/analysis/:ticker" 
                    element={
                        <ErrorBoundary>
                            <Dashboard />
                        </ErrorBoundary>
                    } 
                />
                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </main>
    </div>
  );
}

export default App;
