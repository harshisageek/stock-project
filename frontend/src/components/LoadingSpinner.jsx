/**
 * LoadingSpinner Component
 * 
 * Animated loading spinner with "Scanning Market Data..." text
 */

import { Loader2 } from 'lucide-react';

function LoadingSpinner() {
    return (
        <div className="flex flex-col items-center justify-center py-16">
            {/* Animated spinner container */}
            <div className="relative mb-6">
                {/* Outer glow ring */}
                <div
                    className="absolute inset-0 rounded-full animate-pulse-glow"
                    style={{
                        background: 'radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%)',
                        width: '120px',
                        height: '120px',
                        left: '-10px',
                        top: '-10px',
                    }}
                />

                {/* Spinning loader */}
                <Loader2
                    size={100}
                    className="animate-spin-slow"
                    style={{
                        color: 'var(--accent-cyan)',
                        filter: 'drop-shadow(0 0 20px rgba(0, 212, 255, 0.5))'
                    }}
                />
            </div>

            {/* Analyzing text */}
            <p
                className="text-lg animate-pulse-glow"
                style={{ color: 'var(--accent-cyan)' }}
            >
                Analyzing...
            </p>

            {/* Main loading text */}
            <h2
                className="text-2xl font-semibold mt-4"
                style={{ color: 'var(--text-primary)' }}
            >
                Scanning Market Data...
            </h2>
        </div>
    );
}

export default LoadingSpinner;
