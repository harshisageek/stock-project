import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CrosshairMode, CandlestickSeries, HistogramSeries, AreaSeries } from 'lightweight-charts';

const StockChart = ({ data, chartType = 'pro' }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);
    const tooltipRef = useRef(null);

    useEffect(() => {
        if (!data || data.length === 0 || !chartContainerRef.current) return;

        // 1. Transform Data
        const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

        // 2. Create Chart
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: '#161a1e' },
                textColor: '#848e9c',
            },
            grid: {
                vertLines: { color: '#2b3139' },
                horzLines: { color: '#2b3139' },
            },
            width: chartContainerRef.current.clientWidth,
            height: 500,
            crosshair: {
                mode: CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#2b3139',
            },
            timeScale: {
                borderColor: '#2b3139',
                timeVisible: true,
            },
        });

        // 3. Add Series
        let mainSeries;
        
        if (chartType === 'simple') {
            const areaData = sortedData.map(d => ({
                time: d.date.split('T')[0],
                value: d.close,
                // store extras for tooltip
                original: d 
            }));

            // Determine Trend
            const firstPrice = areaData[0]?.value || 0;
            const lastPrice = areaData[areaData.length - 1]?.value || 0;
            const isUp = lastPrice >= firstPrice;
            const lineColor = isUp ? '#0ecb81' : '#f6465d';

            mainSeries = chart.addSeries(AreaSeries, {
                lineColor: lineColor,
                topColor: lineColor,
                bottomColor: isUp ? 'rgba(14, 203, 129, 0.05)' : 'rgba(246, 70, 93, 0.05)',
                lineWidth: 2,
            });
            mainSeries.setData(areaData);
        } else {
            const candleData = sortedData.map(d => ({
                time: d.date.split('T')[0],
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close,
                // store extras
                original: d
            }));

            mainSeries = chart.addSeries(CandlestickSeries, {
                upColor: '#0ecb81',
                downColor: '#f6465d',
                borderVisible: false,
                wickUpColor: '#0ecb81',
                wickDownColor: '#f6465d',
            });
            mainSeries.setData(candleData);
        }

        // 4. Add Volume
        const volumeData = sortedData.map(d => ({
            time: d.date.split('T')[0],
            value: d.volume,
            color: d.close >= d.open ? 'rgba(14, 203, 129, 0.5)' : 'rgba(246, 70, 93, 0.5)',
        }));

        const volumeSeries = chart.addSeries(HistogramSeries, {
            priceFormat: { type: 'volume' },
            priceScaleId: '', 
            scaleMargins: { top: 0.8, bottom: 0 },
        });
        volumeSeries.setData(volumeData);

        chart.timeScale().fitContent();
        chartRef.current = chart;

        // --- TOOLTIP LOGIC ---
        chart.subscribeCrosshairMove(param => {
            if (!tooltipRef.current) return;
            
            if (
                param.point === undefined ||
                !param.time ||
                param.point.x < 0 ||
                param.point.x > chartContainerRef.current.clientWidth ||
                param.point.y < 0 ||
                param.point.y > chartContainerRef.current.clientHeight
            ) {
                tooltipRef.current.style.display = 'none';
                return;
            }

            // Get data from series
            const priceData = param.seriesData.get(mainSeries);
            const volumeDataPoint = param.seriesData.get(volumeSeries);
            
            if (priceData) {
                const dateStr = param.time;
                const close = priceData.close !== undefined ? priceData.close : priceData.value;
                const vol = volumeDataPoint ? volumeDataPoint.value : 0;

                tooltipRef.current.style.display = 'block';
                tooltipRef.current.innerHTML = `
                    <div class="font-mono text-xs">
                        <div class="font-bold text-[var(--text-secondary)] mb-1">${dateStr}</div>
                        <div class="flex flex-col gap-1">
                            <div class="flex justify-between gap-4">
                                <span class="text-[var(--text-secondary)]">Price:</span> 
                                <span class="text-[var(--text-primary)] font-bold">${close.toFixed(2)}</span>
                            </div>
                            <div class="flex justify-between gap-4">
                                <span class="text-[var(--text-secondary)]">Vol:</span> 
                                <span class="text-[#f0b90b]">${(vol / 1000000).toFixed(2)}M</span>
                            </div>
                        </div>
                    </div>
                `;
            }
        });

        // Resize
        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data, chartType]);

    return (
        <div className="relative w-full h-[500px]">
            <div ref={chartContainerRef} className="w-full h-full" />
            <div 
                ref={tooltipRef}
                className="absolute top-3 left-3 z-20 pointer-events-none bg-[var(--bg-card)]/90 backdrop-blur-sm border border-[var(--border-color)] p-2 rounded shadow-lg hidden"
            ></div>
        </div>
    );
};

export default StockChart;
