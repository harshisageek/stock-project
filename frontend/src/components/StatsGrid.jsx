const StatRow = ({ label, value, isCurrency = false }) => (
    <div className="flex justify-between py-2 border-b border-dashed border-gray-200 dark:border-gray-700 last:border-0">
        <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
        <span className="text-sm font-medium font-mono text-gray-900 dark:text-gray-100">
            {isCurrency ? `$${value.toLocaleString()}` : value.toLocaleString()}
        </span>
    </div>
);

const StatsGrid = ({ data }) => {
    if (!data || data.length === 0) return null;
    
    const latest = data[data.length - 1];
    const prev = data[0]; // Simplified calculation for demo
    
    // Mocking some 'Order Book' style depth if not available
    const marketCap = (latest.price * 150000000).toLocaleString(); // Mock cap

    return (
        <div className="space-y-1">
            <StatRow label="24h High" value={latest.high} isCurrency />
            <StatRow label="24h Low" value={latest.low} isCurrency />
            <StatRow label="Volume" value={latest.volume} />
            <StatRow label="Open" value={latest.open} isCurrency />
            <StatRow label="Close" value={latest.close} isCurrency />
        </div>
    );
};

export default StatsGrid;