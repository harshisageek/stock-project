import pandas as pd
import numpy as np

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Moving Average Convergence Divergence"""
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({'MACD': macd, 'MACD_Signal': signal_line})

def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
    """
    Returns Raw Bands (for Trend Logic) AND %B (for ML).
    %B = (Price - Lower) / (Upper - Lower)
    """
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    # %B (Normalized Position within bands) - Good for ML
    pct_b = (series - lower) / (upper - lower)
    
    return pd.DataFrame({
        'BB_Upper': upper, 
        'BB_Lower': lower, 
        'BB_Middle': middle,
        'BB_Pct': pct_b
    })

def calculate_sma(series: pd.Series, period: int = 50) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=period).mean()

def calculate_sma_ratio(series: pd.Series, period: int = 50) -> pd.Series:
    """Ratio of Price to SMA. > 1.0 means uptrend."""
    sma = series.rolling(window=period).mean()
    return series / sma

def calculate_log_returns(series: pd.Series) -> pd.Series:
    """Log Returns = ln(P_t / P_t-1). Better statistical properties than % change."""
    return np.log(series / series.shift(1))

def calculate_volatility_ratio(series: pd.Series, short_window: int = 5, long_window: int = 20) -> pd.Series:
    """Ratio of Short-term Volatility to Long-term Volatility. >1 means expanding volatility."""
    returns = series.pct_change()
    short_vol = returns.rolling(window=short_window).std()
    long_vol = returns.rolling(window=long_window).std()
    return short_vol / long_vol

def calculate_roc(series: pd.Series, period: int = 10) -> pd.Series:
    """Rate of Change"""
    return series.pct_change(periods=period) * 100

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range (Volatility Magnitude)"""
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    return true_range.rolling(window=period).mean()

def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """Commodity Channel Index (Cyclical Trends)"""
    tp = (high + low + close) / 3
    sma = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    
    # Avoid division by zero
    cci = (tp - sma) / (0.015 * mad + 1e-6)
    return cci

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds all technical indicators to the DataFrame.
    Returns both Raw indicators (for Logic) and Normalized ones (for ML).
    """
    df = df.copy()
    
    col_map = {c.lower(): c for c in df.columns}
    close_col = col_map.get('close', 'Close')
    high_col = col_map.get('high', 'High')
    low_col = col_map.get('low', 'Low')
    
    if close_col not in df.columns:
        return df 
        
    close = df[close_col].astype(float)
    high = df[high_col].astype(float) if high_col in df.columns else close
    low = df[low_col].astype(float) if low_col in df.columns else close
    
    # 1. Momentum / Oscillators
    df['RSI'] = calculate_rsi(close)
    df['ROC'] = calculate_roc(close)
    df['CCI'] = calculate_cci(high, low, close)
    
    # 2. Trend (MACD)
    macd_df = calculate_macd(close)
    df = pd.concat([df, macd_df], axis=1)
    
    # 3. Volatility (Bollinger & ATR)
    bb_df = calculate_bollinger_bands(close)
    df = pd.concat([df, bb_df], axis=1)
    
    atr = calculate_atr(high, low, close)
    df['ATR_Pct'] = atr / close # Normalized ATR (Volatility relative to price)
    
    # 4. Moving Averages (for Trend Logic)
    df['SMA_50'] = calculate_sma(close, 50)
    
    # 5. Advanced Stationary Features (For ML)
    df['Log_Ret'] = calculate_log_returns(close)
    df['Vol_Ratio'] = calculate_volatility_ratio(close)
    df['SMA_Ratio'] = calculate_sma_ratio(close)
    
    # 6. Lagged Returns (Short-term memory helper)
    # The LSTM sees sequence, but explicit features help
    df['Ret_1d'] = df['Log_Ret'].shift(1)
    df['Ret_3d'] = close.pct_change(3)
    df['Ret_5d'] = close.pct_change(5)
    df['Ret_10d'] = close.pct_change(10)
    df['Ret_20d'] = close.pct_change(20)
    
    return df