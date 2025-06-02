import numpy as np
from typing import List, Dict, Optional, Tuple
import pandas as pd
from asyncio import Lock


class TechnicalAnalysis:
    """Technical analysis calculations class"""

    def __init__(self):
        self.lock = Lock()  # Add lock for thread safety in async operations

    @staticmethod
    async def calculate_vwap(candles: List[Dict], period: int = 24) -> List[float]:
        """Enhanced VWAP with configurable period and numpy optimization"""
        if not candles:
            return []

        # Convert to numpy arrays for faster calculation
        typical_prices = np.array([(c['high'] + c['low'] + c['close']) / 3 for c in candles])
        volumes = np.array([c['volume'] for c in candles])

        # Calculate rolling VWAP
        cumul_tp_vol = np.multiply(typical_prices, volumes)
        cumul_vol = volumes.cumsum()
        vwap = np.divide(cumul_tp_vol.cumsum(), cumul_vol, where=cumul_vol != 0)

        return vwap.tolist()

    @staticmethod
    async def calculate_rsi(closes: List[float], period: int = 14) -> List[float]:
        """Calculate RSI values"""
        if not closes:
            return []

        deltas = np.diff(closes)
        seed = deltas[:period + 1]

        # Handle zero case
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period

        if down == 0:
            rs = float('inf')
        else:
            rs = up / down

        rsi = np.zeros_like(closes)
        rsi[:period] = 100. - 100. / (1. + rs)

        for i in range(period, len(closes)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period

            if down == 0:
                rs = float('inf')
            else:
                rs = up / down

            rsi[i] = 100. - 100. / (1. + rs)

        return rsi.tolist()

    @staticmethod
    async def calculate_macd(closes: List[float]) -> Tuple[List[float], List[float], List[float]]:
        """Calculate MACD, Signal, and Histogram"""
        if not closes:
            return [], [], []

        exp1 = pd.Series(closes).ewm(span=12, adjust=False).mean()
        exp2 = pd.Series(closes).ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return macd.tolist(), signal.tolist(), hist.tolist()

    @staticmethod
    async def calculate_bollinger_bands(closes: List[float], period: int = 20) -> Tuple[
        List[float], List[float], List[float]]:
        """Calculate Bollinger Bands"""
        if not closes:
            return [], [], []

        closes_series = pd.Series(closes)
        mid_band = closes_series.rolling(window=period).mean()
        std_dev = closes_series.rolling(window=period).std()
        upper_band = mid_band + (std_dev * 2)
        lower_band = mid_band - (std_dev * 2)
        return upper_band.tolist(), mid_band.tolist(), lower_band.tolist()

    @staticmethod
    async def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[
        float]:
        """Calculate Average True Range"""
        if not any([highs, lows, closes]):
            return []

        tr = []
        for i in range(len(closes)):
            if i == 0:
                tr.append(highs[i] - lows[i])
            else:
                tr1 = highs[i] - lows[i]
                tr2 = abs(highs[i] - closes[i - 1])
                tr3 = abs(lows[i] - closes[i - 1])
                tr.append(max(tr1, tr2, tr3))

        atr = pd.Series(tr).rolling(window=period).mean().tolist()
        return atr

    @staticmethod
    async def calculate_stochastic(highs: List[float], lows: List[float], closes: List[float],
                                   k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Calculate Stochastic Oscillator"""
        if not any([highs, lows, closes]):
            return [], []

        lowest_low = pd.Series(lows).rolling(window=k_period).min()
        highest_high = pd.Series(highs).rolling(window=k_period).max()

        # Handle division by zero
        denom = highest_high - lowest_low
        denom = denom.replace(0, float('inf'))

        k = 100 * ((pd.Series(closes) - lowest_low) / denom)
        d = k.rolling(window=d_period).mean()

        return k.tolist(), d.tolist()

    @staticmethod
    async def calculate_obv(closes: List[float], volumes: List[float]) -> List[float]:
        """Calculate On-Balance Volume"""
        if not closes or not volumes:
            return []

        obv = [0]
        for i in range(1, len(closes)):
            if closes[i] > closes[i - 1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i - 1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        return obv

    @staticmethod
    async def calculate_pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
        """Calculate Pivot Points and Support/Resistance levels"""
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)

        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }

    @staticmethod
    async def calculate_ichimoku(highs: List[float], lows: List[float],
                                 tenkan_period: int = 9,
                                 kijun_period: int = 26,
                                 senkou_span_b_period: int = 52) -> Dict[str, List[float]]:
        """Calculate Ichimoku Cloud components"""
        if not highs or not lows:
            return {
                'tenkan_sen': [],
                'kijun_sen': [],
                'senkou_span_a': [],
                'senkou_span_b': []
            }

        async def donchian(highs: List[float], lows: List[float], period: int) -> List[float]:
            high_series = pd.Series(highs)
            low_series = pd.Series(lows)
            return ((high_series.rolling(window=period).max() +
                     low_series.rolling(window=period).min()) / 2).tolist()

        tenkan_sen = await donchian(highs, lows, tenkan_period)
        kijun_sen = await donchian(highs, lows, kijun_period)

        # Senkou Span A
        senkou_span_a = [(t + k) / 2 if t is not None and k is not None else None
                         for t, k in zip(tenkan_sen, kijun_sen)]

        # Senkou Span B
        senkou_span_b = await donchian(highs, lows, senkou_span_b_period)

        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b
        }

    @staticmethod
    async def detect_divergence(prices: List[float], indicator_values: List[float],
                                lookback: int = 10) -> Dict[str, bool]:
        """Detect Regular and Hidden Divergences"""
        if len(prices) < lookback or len(indicator_values) < lookback:
            return {
                'regular_bullish': False,
                'regular_bearish': False,
                'hidden_bullish': False,
                'hidden_bearish': False
            }

        # Get last n periods
        recent_prices = prices[-lookback:]
        recent_indicator = indicator_values[-lookback:]

        # Calculate price and indicator trends
        price_trend = recent_prices[-1] > recent_prices[0]
        indicator_trend = recent_indicator[-1] > recent_indicator[0]

        return {
            'regular_bullish': not price_trend and indicator_trend,
            'regular_bearish': price_trend and not indicator_trend,
            'hidden_bullish': price_trend and not indicator_trend,
            'hidden_bearish': not price_trend and indicator_trend
        }


class MarketStructure:
    """Market structure analysis class"""

    def __init__(self):
        self.lock = Lock()  # Add lock for thread safety in async operations

    @staticmethod
    async def identify_swing_points(highs: List[float], lows: List[float],
                                    threshold: float = 0.001) -> Dict[str, List[Tuple[int, float]]]:
        """Identify swing highs and lows"""
        if not highs or not lows or len(highs) < 5 or len(lows) < 5:
            return {'highs': [], 'lows': []}

        swing_highs = []
        swing_lows = []

        for i in range(2, len(highs) - 2):
            # Swing high
            if (highs[i] > highs[i - 1] and highs[i] > highs[i - 2] and
                    highs[i] > highs[i + 1] and highs[i] > highs[i + 2]):
                swing_highs.append((i, highs[i]))

            # Swing low
            if (lows[i] < lows[i - 1] and lows[i] < lows[i - 2] and
                    lows[i] < lows[i + 1] and lows[i] < lows[i + 2]):
                swing_lows.append((i, lows[i]))

        return {'highs': swing_highs, 'lows': swing_lows}

    @staticmethod
    async def analyze_volume_profile(prices: List[float], volumes: List[float],
                                     num_bins: int = 50) -> Dict[str, float]:
        """Analyze volume profile"""
        if not prices or not volumes:
            return {}

        # Create price bins
        min_price = min(prices)
        max_price = max(prices)

        if min_price == max_price:
            return {
                'poc': min_price,
                'value_area_high': min_price,
                'value_area_low': min_price,
                'volume_distribution': {}
            }

        bin_size = (max_price - min_price) / num_bins

        volume_profile = {}
        for price, volume in zip(prices, volumes):
            bin_idx = int((price - min_price) / bin_size)
            if bin_idx not in volume_profile:
                volume_profile[bin_idx] = 0
            volume_profile[bin_idx] += volume

        # Find POC (Point of Control)
        poc_bin = max(volume_profile.items(), key=lambda x: x[1])[0]
        poc_price = min_price + (poc_bin + 0.5) * bin_size

        # Calculate Value Area
        total_volume = sum(volume_profile.values())
        target_volume = total_volume * 0.68  # 68% of volume

        sorted_bins = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
        cumulative_volume = 0
        value_area_bins = []

        for bin_idx, volume in sorted_bins:
            cumulative_volume += volume
            value_area_bins.append(bin_idx)
            if cumulative_volume >= target_volume:
                break

        value_area_high = min_price + (max(value_area_bins) + 1) * bin_size
        value_area_low = min_price + min(value_area_bins) * bin_size

        return {
            'poc': poc_price,
            'value_area_high': value_area_high,
            'value_area_low': value_area_low,
            'volume_distribution': dict(sorted(volume_profile.items()))
        }
    