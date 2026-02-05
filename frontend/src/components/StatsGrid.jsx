const StatRow = ({ label, value, isCurrency = false, color }) => (
    <div className="flex justify-between items-center py-3 border-b border-[var(--border-color)] last:border-0 hover:bg-[var(--bg-secondary)] px-2 transition-colors">
        <span className="text-sm text-[var(--text-secondary)] font-medium">{label}</span>
        <span className={`text-sm font-bold font-mono ${color ? color : 'text-[var(--text-primary)]'}`}>
            {isCurrency 
                ? `$${Number(value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}` 
                : Number(value).toLocaleString()}
        </span>
    </div>
);

const StatsGrid = ({ data }) => {
    if (!data || data.length === 0) return null;
    
    const latest = data[data.length - 1];
    
    return (
        <div className="flex flex-col w-full">
            <StatRow label="Open" value={latest.open} isCurrency />
            <StatRow label="Day High" value={latest.high} isCurrency />
            <StatRow label="Day Low" value={latest.low} isCurrency />
            <StatRow label="Volume" value={latest.volume} />
            <StatRow label="Prev. Close" value={latest.open * 0.995} isCurrency /> {/* Mock */}
        </div>
    );
};

export default StatsGrid;
