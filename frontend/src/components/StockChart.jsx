import { 
    ComposedChart, 
    Area, 
    Bar, 
    XAxis, 
    YAxis, 
    Tooltip, 
    ResponsiveContainer, 
    CartesianGrid,
    ReferenceLine,
    Cell
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        // Find data
        const priceData = payload.find(p => p.dataKey === 'price');
        const dataPoint = priceData ? priceData.payload : {};
        const isUp = dataPoint.close >= dataPoint.open;
        const color = isUp ? '#0ecb81' : '#f6465d';

        return (
            <div className="bg-[#1e2329] border border-gray-700 p-3 rounded-lg shadow-2xl text-xs min-w-[180px] z-50">
                <p className="font-mono text-gray-400 mb-2 border-b border-gray-700 pb-1">{label}</p>
                
                <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                    <span className="text-gray-500">Price:</span>
                    <span className={`font-bold text-right`} style={{ color }}>
                        ${dataPoint.price?.toFixed(2)}
                    </span>
                    
                    <span className="text-gray-500">Open:</span>
                    <span className="text-gray-300 text-right">${dataPoint.open?.toFixed(2)}</span>
                    
                    <span className="text-gray-500">High:</span>
                    <span className="text-gray-300 text-right">${dataPoint.high?.toFixed(2)}</span>
                    
                    <span className="text-gray-500">Low:</span>
                    <span className="text-gray-300 text-right">${dataPoint.low?.toFixed(2)}</span>
                    
                    <span className="text-gray-500">Vol:</span>
                    <span className={`text-right ${isUp ? 'text-[#0ecb81]' : 'text-[#f6465d]'}`}>
                        {(dataPoint.volume / 1000000).toFixed(1)}M
                    </span>
                </div>
            </div>
        );
    }
    return null;
};

const StockChart = ({ data }) => {
    if (!data || data.length === 0) return null;

    // Determine overall trend color for the Area fill
    const first = data[0].price;
    const last = data[data.length - 1].price;
    const isPositive = last >= first;
    const mainColor = isPositive ? '#0ecb81' : '#f6465d';

    return (
        <div className="w-full h-[500px] select-none bg-[#161a1e] rounded-lg">
            <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={mainColor} stopOpacity={0.25}/>
                            <stop offset="95%" stopColor={mainColor} stopOpacity={0}/>
                        </linearGradient>
                    </defs>
                    
                    {/* Finer Grid */}
                    <CartesianGrid strokeDasharray="3 3" vertical={true} stroke="#2b3139" opacity={0.4} />
                    
                    <XAxis 
                        dataKey="date" 
                        tickFormatter={(str) => {
                            const date = new Date(str);
                            return `${date.getDate()} ${date.toLocaleString('default', { month: 'short' })}`;
                        }}
                        tick={{ fontSize: 10, fill: '#848e9c' }}
                        axisLine={false}
                        tickLine={false}
                        minTickGap={40}
                        dy={10}
                    />

                    {/* Volume Axis (Hidden) */}
                    <YAxis 
                        yAxisId="volume"
                        orientation="left"
                        domain={[0, 'dataMax * 3']} 
                        hide={true} 
                    />

                    {/* Price Axis (Right) */}
                    <YAxis 
                        yAxisId="price"
                        domain={['auto', 'auto']}
                        orientation="right"
                        tick={{ fontSize: 11, fill: '#848e9c' }}
                        tickFormatter={(val) => val.toFixed(2)}
                        axisLine={false}
                        tickLine={false}
                        tickCount={8}
                        width={50}
                    />

                    <Tooltip 
                        content={<CustomTooltip />} 
                        cursor={{ stroke: '#848e9c', strokeWidth: 1, strokeDasharray: '4 4' }}
                        isAnimationActive={false}
                    />

                    {/* Colored Volume Bars */}
                    <Bar yAxisId="volume" dataKey="volume" barSize={4}>
                        {data.map((entry, index) => (
                            <Cell 
                                key={`cell-${index}`} 
                                fill={entry.close >= entry.open ? '#0ecb81' : '#f6465d'} 
                                opacity={0.5}
                            />
                        ))}
                    </Bar>

                    {/* Sharp Price Line */}
                    <Area 
                        yAxisId="price"
                        type="linear" // Sharp lines (Binance style)
                        dataKey="price" 
                        stroke={mainColor} 
                        strokeWidth={2}
                        fill="url(#colorPrice)"
                        activeDot={{ r: 4, stroke: '#fff', strokeWidth: 2, fill: mainColor }}
                        isAnimationActive={true}
                    />
                    
                    {/* Dotted Reference Line (Previous Close equivalent) */}
                    <ReferenceLine y={first} yAxisId="price" stroke="#848e9c" strokeDasharray="3 3" opacity={0.5} />
                    
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
};

export default StockChart;
