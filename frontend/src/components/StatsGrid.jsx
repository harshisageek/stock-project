/**
 * StatsGrid Component
 * 
 * Displays key stock statistics (Open, High, Low, Volume)
 * using a glassmorphism grid layout.
 */
import { ArrowUp, ArrowDown, Activity, BarChart2 } from 'lucide-react';

function StatsGrid({ data }) {
    if (!data || data.length === 0) return null;

    // Get latest data point (assuming data is sorted or we take the last one)
    // Based on app.py: graph_data.reverse() # Oldest first
    // So the last element is the latest/current day.
    const latest = data[data.length - 1];

    // Calculate High/Low for the selected range (based on the passed data array)
    const rangeHigh = Math.max(...data.map(d => d.high));
    const rangeLow = Math.min(...data.map(d => d.low));

    // Format volume (e.g., 24.5M)
    const formatVolume = (num) => {
        if (num >= 1.0e+9) {
            return (num / 1.0e+9).toFixed(1) + "B";
        }
        if (num >= 1.0e+6) {
            return (num / 1.0e+6).toFixed(1) + "M";
        }
        if (num >= 1.0e+3) {
            return (num / 1.0e+3).toFixed(1) + "K";
        }
        return num;
    };

    const stats = [
        {
            label: "Open",
            value: latest.open,
            prefix: "$",
            icon: <Activity className="w-4 h-4 text-blue-400" />,
            color: "text-blue-200"
        },
        {
            label: "High (Range)",
            value: rangeHigh,
            prefix: "$",
            icon: <ArrowUp className="w-4 h-4 text-green-400" />,
            color: "text-green-200"
        },
        {
            label: "Low (Range)",
            value: rangeLow,
            prefix: "$",
            icon: <ArrowDown className="w-4 h-4 text-red-400" />,
            color: "text-red-200"
        },
        {
            label: "Volume",
            value: formatVolume(latest.volume),
            prefix: "",
            icon: <BarChart2 className="w-4 h-4 text-purple-400" />,
            color: "text-purple-200"
        }
    ];

    return (
        <div className="grid grid-cols-4 gap-4 mt-4">
            {stats.map((stat, idx) => (
                <div key={idx} className="flex flex-col">
                    <span className="text-[10px] text-gray-400 uppercase tracking-wider mb-0.5">{stat.label}</span>
                    <span className={`text-lg font-bold truncate ${stat.color}`}>
                        {/* Only add prefix if it's not volume/raw number or handle logic inside format */}
                        {stat.prefix}{typeof stat.value === 'number' ? stat.value.toFixed(2) : stat.value}
                    </span>
                </div>
            ))}
        </div>
    );
}

export default StatsGrid;
