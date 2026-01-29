const StatRow = ({ label, value, isCurrency = false, color }) => (
    <div className="flex justify-between items-center py-1.5">
        <span className="text-xs text-[#848e9c]">{label}</span>
        <span className={`text-xs font-mono font-medium ${color ? color : 'text-[#eaecef]'}`}>
            {isCurrency ? `$${Number(value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : Number(value).toLocaleString()}
        </span>
    </div>
);

const StatsGrid = ({ data }) => {
    if (!data || data.length === 0) return null;
    
    const latest = data[data.length - 1];
    
    return (
        <div className="flex flex-col gap-0.5">
            <StatRow label="24h High" value={latest.high} isCurrency />
            <StatRow label="24h Low" value={latest.low} isCurrency />
            <StatRow label="24h Volume" value={latest.volume} />
            <StatRow label="Open Price" value={latest.open} isCurrency />
            <StatRow label="Prev Close" value={latest.open * 0.99} isCurrency /> {/* Mock prev close */}
        </div>
    );
};

export default StatsGrid;
