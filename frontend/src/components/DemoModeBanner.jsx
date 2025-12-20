/**
 * DemoModeBanner Component
 * 
 * Yellow/orange warning banner for circuit breaker mode
 */

import { AlertTriangle } from 'lucide-react';

function DemoModeBanner() {
    return (
        <div className="demo-banner animate-slide-down fixed top-0 left-0 right-0 z-50 px-4 py-2.5">
            <div className="flex items-center justify-center gap-2 text-white font-medium">
                <AlertTriangle size={18} />
                <span>Demo Mode Active: Live market data is currently unavailable. Showing historical snapshot.</span>
            </div>
        </div>
    );
}

export default DemoModeBanner;
