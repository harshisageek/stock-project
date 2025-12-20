import React from 'react';

const SentimentGauge = ({ score }) => {
    // Sanitize score to be within -100 to 100
    const val = Math.max(-100, Math.min(100, score || 0));

    // Determine Color and Text
    let colorClass = "text-yellow-400";
    let text = "NEUTRAL";

    if (val >= 60) {
        colorClass = "text-green-400";
        text = "STRONG BUY";
    } else if (val > 20) {
        colorClass = "text-green-300";
        text = "BUY";
    } else if (val >= -20) {
        colorClass = "text-yellow-400";
        text = "NEUTRAL";
    } else if (val > -60) {
        colorClass = "text-red-300";
        text = "SELL";
    } else {
        colorClass = "text-red-400";
        text = "STRONG SELL";
    }

    return (
        <div className="flex flex-col items-center justify-center p-4 h-full">
            <h3 className="text-xs text-gray-400 mb-2 uppercase tracking-widest font-semibold text-center">
                Quant Analysis (-100 to +100)
            </h3>

            <div className="flex flex-col items-center justify-center flex-grow">
                {/* Score Number */}
                <span className={`text-7xl font-extrabold tracking-tighter drop-shadow-lg ${colorClass}`}>
                    {val > 0 ? `+${val.toFixed(0)}` : val.toFixed(0)}
                </span>

                {/* Verdict Text */}
                <span className={`text-sm font-bold tracking-[0.2em] mt-2 uppercase ${colorClass}`}>
                    {text}
                </span>
            </div>
        </div>
    );
};

export default SentimentGauge;
