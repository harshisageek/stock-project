import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CrosshairMode, CandlestickSeries, HistogramSeries } from 'lightweight-charts';

const StockChart = ({ data }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);

    useEffect(() => {
        if (!data || data.length === 0 || !chartContainerRef.current) return;

        // 1. Transform Data
        const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

        const candleData = sortedData.map(d => ({
            time: d.date.split('T')[0], // YYYY-MM-DD
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
        }));

        const volumeData = sortedData.map(d => ({
            time: d.date.split('T')[0],
            value: d.volume,
            color: d.close >= d.open ? 'rgba(14, 203, 129, 0.5)' : 'rgba(246, 70, 93, 0.5)',
        }));

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

        // 3. Add Series (v5 Syntax)
        const candlestickSeries = chart.addSeries(CandlestickSeries, {
            upColor: '#0ecb81',
            downColor: '#f6465d',
            borderVisible: false,
            wickUpColor: '#0ecb81',
            wickDownColor: '#f6465d',
        });
        candlestickSeries.setData(candleData);

        const volumeSeries = chart.addSeries(HistogramSeries, {
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '', // Overlay
            scaleMargins: {
                top: 0.8, 
                bottom: 0,
            },
        });
        volumeSeries.setData(volumeData);

        chartRef.current = chart;

        // 4. Resize Handler
        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data]);

    return (
        <div 
            ref={chartContainerRef} 
            className="w-full h-[500px] relative"
        />
    );
};

export default StockChart;
