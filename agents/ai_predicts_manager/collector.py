import asyncio
import logging
from datetime import datetime

import aiohttp
import ccxt.async_support as ccxt

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AsyncRateLimiter:
    def __init__(self):
        self.limits = {
            "binance": {"calls": 0, "window_start": datetime.now().timestamp(), "limit": 1200, "window": 60},
            "coingecko": {"calls": 0, "window_start": datetime.now().timestamp(), "limit": 50, "window": 60},
        }
        self.locks = {"binance": asyncio.Lock(), "coingecko": asyncio.Lock()}

    async def check_and_wait(self, api: str):
        async with self.locks[api]:
            current_time = datetime.now().timestamp()
            limit_info = self.limits[api]

            if current_time - limit_info["window_start"] > limit_info["window"]:
                limit_info["calls"] = 0
                limit_info["window_start"] = current_time

            if limit_info["calls"] >= limit_info["limit"]:
                sleep_time = limit_info["window_start"] + limit_info["window"] - current_time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    limit_info["calls"] = 0
                    limit_info["window_start"] = datetime.now().timestamp()

            limit_info["calls"] += 1


class AsyncDataCollector:
    def __init__(self):
        self.binance = ccxt.binance(
            {
                "enableRateLimit": True,
                "options": {"defaultType": "spot", "adjustForTimeDifference": True, "recvWindow": 60000},
                "timeout": 30000,
            }
        )
        self.futures_base_url = "https://fapi.binance.com"
        self.rate_limiter = AsyncRateLimiter()
        self.sr_threshold = 0.005
        self.whale_threshold = 50000
        self.ignored_symbols = ["USDT", "USDC", "BUSD", "DAI", "TUSD", "STETH"]
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        await self.binance.close()

    async def _check_market_exists(self, symbol_market: str) -> bool:
        """Verify market existence with error handling"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            markets = await self.binance.load_markets()

            formatted_symbol = symbol_market.replace("/", "")

            for market in markets:
                if market.replace("/", "") == formatted_symbol:
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking market existence: {str(e)}")
            return False

    async def get_top_coins(self, limit: int = 5) -> list[dict]:
        """Get top N coins by market cap from CoinGecko"""
        try:
            await self.rate_limiter.check_and_wait("coingecko")
            async with self.session.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1},
            ) as response:
                response.raise_for_status()
                all_coins = await response.json()
                filtered_coins = [coin for coin in all_coins if coin["symbol"].upper() not in self.ignored_symbols]
                return filtered_coins[:limit]
        except Exception as e:
            logger.error(f"Error fetching top coins: {str(e)}")
            return []

    async def get_candle_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> list[dict] | None:
        """Get OHLCV data with improved error handling"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            symbol_market = f"{symbol}/USDT"

            # Try spot market first
            try:
                ohlcv = await self.binance.fetch_ohlcv(symbol=symbol_market, timeframe=timeframe, limit=limit)

                if ohlcv and len(ohlcv) > 0:
                    logger.info(f"Successfully fetched {len(ohlcv)} candles for {symbol}")
                    return await self._format_ohlcv(ohlcv)

            except Exception as spot_error:
                logger.warning(f"Spot market fetch failed for {symbol}: {str(spot_error)}")

                # Try futures market as fallback
                try:
                    futures_symbol = f"{symbol}USDT"
                    ohlcv = await self.binance.fetch_ohlcv(
                        symbol=futures_symbol, timeframe=timeframe, limit=limit, params={"type": "future"}
                    )

                    if ohlcv and len(ohlcv) > 0:
                        logger.info(f"Successfully fetched {len(ohlcv)} futures candles for {symbol}")
                        return await self._format_ohlcv(ohlcv)

                except Exception as futures_error:
                    logger.warning(f"Futures market fetch failed for {symbol}: {str(futures_error)}")

            logger.warning(f"No candle data retrieved for {symbol} in any market")
            return None

        except Exception as e:
            logger.error(f"Error fetching candle data for {symbol}: {str(e)}")
            return None

    async def _calculate_sr_levels(self, candles: list[dict], num_levels: int = 5) -> dict[str, list[dict]]:
        """Improved support/resistance calculation with volume weighting"""
        if not candles:
            return {"support": [], "resistance": []}

        price_levels = {}
        current_price = candles[-1]["close"]
        volume_sum = sum(candle["volume"] for candle in candles)

        if volume_sum == 0:
            return {"support": [], "resistance": []}

        for candle in candles:
            volume_weight = candle["volume"] / volume_sum

            for price_type in ["high", "low"]:
                price = candle[price_type]
                matched = False

                for level in list(price_levels.keys()):
                    if abs(price - level) / level < self.sr_threshold:
                        data = price_levels[level]
                        weighted_price = (data["price"] * data["volume"] + price * candle["volume"]) / (
                            data["volume"] + candle["volume"]
                        )
                        data.update(
                            {
                                "price": weighted_price,
                                "touches": data["touches"] + 1,
                                "volume": data["volume"] + candle["volume"],
                            }
                        )
                        matched = True
                        break

                if not matched:
                    price_levels[price] = {
                        "price": price,
                        "touches": 1,
                        "volume": candle["volume"],
                        "type": "resistance" if price > current_price else "support",
                    }

        # Calculate significance scores
        for level in price_levels.values():
            level["significance"] = (
                level["touches"] * level["volume"] * (1 + abs(level["price"] - current_price) / current_price)
            )

        # Split and sort levels
        levels = list(price_levels.values())
        support = sorted([l for l in levels if l["type"] == "support"], key=lambda x: x["significance"], reverse=True)[
            :num_levels
        ]

        resistance = sorted(
            [l for l in levels if l["type"] == "resistance"], key=lambda x: x["significance"], reverse=True
        )[:num_levels]

        return {"support": support, "resistance": resistance}

    async def _normalize_significance(self, levels: list[dict]) -> list[dict]:
        """Normalize significance scores to 0-1 range"""
        if not levels:
            return []

        significances = [level["significance"] for level in levels]
        min_sig = min(significances)
        max_sig = max(significances)

        if max_sig == min_sig:
            return [{**level, "significance": 1.0} for level in levels]

        normalized = []
        for level in levels:
            normalized_significance = (level["significance"] - min_sig) / (max_sig - min_sig)
            normalized.append({**level, "significance": normalized_significance})

        return normalized

    async def _validate_sr_levels(self, levels: dict[str, list[dict]]) -> dict[str, list[dict]]:
        """Validate and normalize support/resistance levels"""
        result = {}
        for level_type in ["support", "resistance"]:
            if level_type not in levels:
                result[level_type] = []
            else:
                result[level_type] = await self._normalize_significance(levels[level_type])

            result[level_type] = sorted(result[level_type], key=lambda x: x["significance"], reverse=True)[:5]

        return result

    async def _debug_sr_levels(self, symbol: str, timeframe: str, levels: dict[str, list[dict]]):
        """Debug support/resistance levels"""
        logger.debug(f"\nS/R Levels for {symbol} ({timeframe}):")
        for level_type in ["support", "resistance"]:
            logger.debug(f"\n{level_type.capitalize()} Levels:")
            for level in levels[level_type]:
                logger.debug(
                    f"Price: {level['price']:.2f}, "
                    f"Touches: {level['touches']}, "
                    f"Volume: {level['volume']:.2f}, "
                    f"Significance: {level['significance']:.4f}"
                )

    async def get_order_book(self, symbol: str, limit: int = 100) -> dict | None:
        """Enhanced order book data collection with grouped orders and volume analysis"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            symbol_market = f"{symbol}/USDT"

            # Verify market exists
            if not await self._check_market_exists(symbol_market):
                logger.warning(f"Market {symbol_market} does not exist")
                return None

            # Fetch order book
            order_book = await self.binance.fetch_order_book(symbol_market, limit)

            if not order_book or not order_book["bids"] or not order_book["asks"]:
                logger.warning(f"Empty order book received for {symbol}")
                return None

            # Group orders to reduce noise
            grouped_bids = await self._group_orders(order_book["bids"])
            grouped_asks = await self._group_orders(order_book["asks"])

            if not grouped_bids or not grouped_asks:
                logger.warning(f"No valid orders after grouping for {symbol}")
                return None

            # Calculate weighted average prices for top N levels
            top_n = 5
            weighted_bid = sum(bid[0] * bid[1] for bid in grouped_bids[:top_n]) / sum(
                bid[1] for bid in grouped_bids[:top_n]
            )
            weighted_ask = sum(ask[0] * ask[1] for ask in grouped_asks[:top_n]) / sum(
                ask[1] for ask in grouped_asks[:top_n]
            )

            # Calculate additional metrics
            bid_volume = sum(bid[1] for bid in grouped_bids)
            ask_volume = sum(ask[1] for ask in grouped_asks)
            spread = ((weighted_ask - weighted_bid) / weighted_bid) * 100
            depth_ratio = bid_volume / ask_volume if ask_volume else 0

            # Calculate volume weighted mid price
            total_volume = bid_volume + ask_volume
            vwmp = ((weighted_bid * ask_volume) + (weighted_ask * bid_volume)) / total_volume if total_volume else 0

            result = {
                "bids": grouped_bids,
                "asks": grouped_asks,
                "bid_ask_spread": spread,
                "depth_ratio": depth_ratio,
                "vwmp": vwmp,
                "metrics": {
                    "bid_volume": bid_volume,
                    "ask_volume": ask_volume,
                    "total_volume": total_volume,
                    "volume_imbalance": (bid_volume - ask_volume) / total_volume if total_volume else 0,
                },
            }

            # Validate the result
            return await self._validate_order_book(result)
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {str(e)}")
            return None

    async def _debug_order_book(self, symbol: str, order_book: dict | None):
        """Debug order book data"""
        if not order_book:
            logger.debug(f"No order book data available for {symbol}")
            return

        logger.debug(f"\nOrder Book for {symbol}:")
        logger.debug(f"Bid/Ask Spread: {order_book['bid_ask_spread']:.4f}%")
        logger.debug(f"Depth Ratio: {order_book['depth_ratio']:.4f}")

        if order_book["bids"] and order_book["asks"]:
            logger.debug(f"Top Bid: {order_book['bids'][0][0]:.2f}")
            logger.debug(f"Top Ask: {order_book['asks'][0][0]:.2f}")
            logger.debug(f"Bid Levels: {len(order_book['bids'])}")
            logger.debug(f"Ask Levels: {len(order_book['asks'])}")

    async def _debug_whale_data(self, symbol: str, whale_data: dict | None):
        """Debug whale trading data with detailed analysis"""
        if not whale_data:
            logger.info(f"🚫 No whale data available for {symbol}")
            return

        logger.info(f"\n🐋 Whale Activity Analysis for {symbol} 🐋")
        logger.info(f"Recent Whale Trades: {len(whale_data['recent_trades'])}")
        logger.info(f"Buy Volume: ${whale_data['buy_volume']:,.2f}")
        logger.info(f"Sell Volume: ${whale_data['sell_volume']:,.2f}")
        logger.info(f"Buy/Sell Ratio: {whale_data['buy_sell_ratio']:.2f}")

        if whale_data["recent_trades"]:
            logger.info("\n📊 Last 5 Whale Trades:")
            for trade in whale_data["recent_trades"][:5]:
                logger.info(
                    f"Time: {trade['time']} | "
                    f"Side: {trade['side']} | "
                    f"Price: ${trade['price']:,.2f} | "
                    f"Size: ${trade['amount_usd']:,.2f}"
                )

    async def _group_orders(self, orders: list[list], group_size: int = 10) -> list[list]:
        """Group orders by price ranges to reduce noise"""
        if not orders:
            return []

        grouped = []
        current_group = {"price": orders[0][0], "volume": 0}

        for price, volume in orders:
            if abs(price - current_group["price"]) <= group_size:
                current_group["volume"] += volume
            else:
                grouped.append([current_group["price"], current_group["volume"]])
                current_group = {"price": price, "volume": volume}

        grouped.append([current_group["price"], current_group["volume"]])
        return grouped

    async def _format_ohlcv(self, ohlcv: list[list]) -> list[dict]:
        """Format OHLCV data with proper typing"""
        return [
            {
                "time": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            }
            for candle in ohlcv
        ]

    async def get_whale_data(self, symbol: str) -> dict | None:
        """Enhanced whale trade detection with dynamic thresholds"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            symbol_market = f"{symbol}/USDT"

            if not await self._check_market_exists(symbol_market):
                return None

            trades = await self.binance.fetch_trades(symbol_market, limit=1000)
            ticker = await self.binance.fetch_ticker(symbol_market)
            current_price = ticker["last"]

            dynamic_threshold = (self.whale_threshold / current_price) * 1000

            whale_trades = []
            buy_volume = 0
            sell_volume = 0

            for trade in trades:
                if trade["amount"] * trade["price"] >= dynamic_threshold:
                    trade_info = {
                        "time": datetime.fromtimestamp(trade["timestamp"] / 1000).isoformat(),
                        "side": trade["side"],
                        "price": trade["price"],
                        "amount": trade["amount"],
                        "amount_usd": trade["price"] * trade["amount"],
                    }
                    whale_trades.append(trade_info)

                    if trade["side"].lower() == "buy":
                        buy_volume += trade_info["amount_usd"]
                    else:
                        sell_volume += trade_info["amount_usd"]

            buy_sell_ratio = buy_volume / sell_volume if sell_volume > 0 else (5.0 if buy_volume > 0 else 1.0)

            return {
                "recent_trades": sorted(whale_trades, key=lambda x: x["time"], reverse=True)[:10],
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
                "buy_sell_ratio": min(buy_sell_ratio, 5.0),
            }
        except Exception as e:
            logger.error(f"Error fetching whale data for {symbol}: {str(e)}")
            return None

    async def get_derivatives_data(self, symbol: str) -> dict:
        """Get comprehensive derivatives data"""
        try:
            symbol_futures = f"{symbol}USDT"

            # Gather all data concurrently
            tasks = [
                self._get_open_interest_direct(symbol_futures),
                self._get_long_short_ratio_direct(symbol_futures),
                self._get_liquidation_levels_direct(symbol_futures),
            ]

            open_interest, long_short_ratio, liquidation_levels = await asyncio.gather(*tasks)

            return {
                "open_interest": open_interest,
                "long_short_ratio": long_short_ratio,
                "liquidation_levels": liquidation_levels,
            }
        except Exception as e:
            logger.error(f"Error fetching derivatives data for {symbol}: {str(e)}")
            return await self._get_empty_derivatives_data()

    async def _get_open_interest_direct(self, symbol: str) -> dict:
        """Get open interest data directly from Binance futures API"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            async with self.session.get(
                f"{self.futures_base_url}/fapi/v1/openInterest", params={"symbol": symbol}
            ) as response:
                response.raise_for_status()
                data = await response.json()

                return {
                    "total": float(data["openInterest"]),
                    "timestamp": datetime.fromtimestamp(data["time"] / 1000).isoformat(),
                }
        except Exception as e:
            logger.error(f"Error fetching open interest: {str(e)}")
            empty_data = await self._get_empty_derivatives_data()
            return empty_data["open_interest"]

    async def _get_long_short_ratio_direct(self, symbol: str) -> dict:
        """Get long/short ratio data directly from Binance futures API"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            async with self.session.get(
                f"{self.futures_base_url}/futures/data/globalLongShortAccountRatio",
                params={"symbol": symbol, "period": "1h"},
            ) as response:
                response.raise_for_status()
                data = (await response.json())[0]

                return {
                    "global": float(data["longShortRatio"]),
                    "long_account": float(data["longAccount"]),
                    "short_account": float(data["shortAccount"]),
                    "timestamp": datetime.fromtimestamp(data["timestamp"] / 1000).isoformat(),
                }
        except Exception as e:
            logger.error(f"Error fetching long/short ratio: {str(e)}")
            empty_data = await self._get_empty_derivatives_data()
            return empty_data["long_short_ratio"]

    async def _get_liquidation_levels_direct(self, symbol: str) -> dict:
        """Get liquidation levels from recent liquidation data"""
        try:
            await self.rate_limiter.check_and_wait("binance")
            async with self.session.get(
                f"{self.futures_base_url}/futures/data/topLongShortPositionRatio",
                params={"symbol": symbol, "period": "1h"},
            ) as response:
                response.raise_for_status()
                data = (await response.json())[:24]

                long_positions = []
                short_positions = []

                for entry in data:
                    try:
                        long_pos = float(entry.get("longPosition", entry.get("longAccount", 0)))
                        short_pos = float(entry.get("shortPosition", entry.get("shortAccount", 0)))

                        if long_pos > 0:
                            long_positions.append(long_pos)
                        if short_pos > 0:
                            short_positions.append(short_pos)
                    except (ValueError, TypeError):
                        continue

                if long_positions and short_positions:
                    return {
                        "long_positions": {
                            "average": sum(long_positions) / len(long_positions),
                            "max": max(long_positions),
                            "min": min(long_positions),
                        },
                        "short_positions": {
                            "average": sum(short_positions) / len(short_positions),
                            "max": max(short_positions),
                            "min": min(short_positions),
                        },
                    }
                logger.warning(f"No valid position data found for {symbol}")
                empty_data = await self._get_empty_derivatives_data()
                return empty_data["liquidation_levels"]

        except Exception as e:
            logger.error(f"Error fetching liquidation levels: {str(e)}")
            empty_data = await self._get_empty_derivatives_data()
            return empty_data["liquidation_levels"]

    async def _get_empty_derivatives_data(self) -> dict:
        """Return empty derivatives data structure for error cases"""
        return {
            "open_interest": {"total": 0.0, "timestamp": datetime.now().isoformat()},
            "long_short_ratio": {
                "global": 1.0,
                "long_account": 0.5,
                "short_account": 0.5,
                "timestamp": datetime.now().isoformat(),
            },
            "liquidation_levels": {
                "long_positions": {"average": 0.0, "max": 0.0, "min": 0.0},
                "short_positions": {"average": 0.0, "max": 0.0, "min": 0.0},
            },
        }

    async def _validate_order_book(self, order_book: dict | None) -> dict | None:
        """Validate and normalize order book data"""
        if not order_book:
            return None

        # Normalize extreme depth ratios
        if order_book.get("depth_ratio", 0) > 5:
            order_book["depth_ratio"] = 5
        elif order_book.get("depth_ratio", 0) < 0.2:
            order_book["depth_ratio"] = 0.2

        # Ensure bid/ask spread is reasonable
        if order_book.get("bid_ask_spread", 0) > 10:  # Cap at 10%
            order_book["bid_ask_spread"] = 10

        return order_book

    async def _validate_whale_data(self, whale_data: dict | None) -> dict | None:
        """Validate and normalize whale data"""
        if not whale_data:
            return None

        # Normalize amounts to USD for consistency
        for trade in whale_data.get("recent_trades", []):
            if "amount_usd" not in trade:
                trade["amount_usd"] = trade["price"] * trade["amount"]

        # Cap extreme buy/sell ratios
        if whale_data.get("buy_sell_ratio", 0) > 10:
            whale_data["buy_sell_ratio"] = 10

        return whale_data

    async def _filter_sr_levels(
        self, levels: dict[str, list[dict]], current_price: float, max_deviation: float = 0.3
    ) -> dict[str, list[dict]]:
        """Filter out S/R levels that are too far from current price"""
        filtered = {"support": [], "resistance": []}

        for level_type in ["support", "resistance"]:
            for level in levels.get(level_type, []):
                # Calculate percentage difference from current price
                price_diff = abs(level["price"] - current_price) / current_price

                # Only keep levels within max_deviation
                if price_diff <= max_deviation:
                    filtered[level_type].append(level)

        return filtered

    async def _calculate_price_changes(self, candles: list[dict]) -> dict[str, float]:
        """Calculate accurate price changes for different timeframes"""
        if not candles or len(candles) < 24:
            return {"1h": 0.0, "24h": 0.0, "7d": 0.0}

        current_price = candles[-1]["close"]
        changes = {
            "1h": ((current_price - candles[-2]["close"]) / candles[-2]["close"]) * 100,
            "24h": ((current_price - candles[-24]["close"]) / candles[-24]["close"]) * 100,
        }

        # 7d change if we have enough data
        if len(candles) >= 168:  # 24 * 7
            changes["7d"] = ((current_price - candles[-168]["close"]) / candles[-168]["close"]) * 100
        else:
            changes["7d"] = 0.0

        return changes

    async def _calculate_risk_metrics(self, timeframes: dict, market_structure: dict) -> dict:
        """Calculate comprehensive risk metrics"""
        # Use 1h timeframe for recent volatility
        hourly_data = timeframes.get("1h", {}).get("technical_analysis", {})

        return {
            "volatility_risk": {
                "current_atr": hourly_data.get("indicators", {}).get("atr", {}).get("current", 0),
                "bb_width": hourly_data.get("indicators", {}).get("bollinger_bands", {}).get("width", 0),
            },
            "momentum_risk": {
                "rsi_extreme": abs(50 - hourly_data.get("indicators", {}).get("rsi", {}).get("current", 50)),
                "macd_histogram": hourly_data.get("indicators", {})
                .get("macd", {})
                .get("current", {})
                .get("histogram", 0),
            },
            "liquidity_risk": {
                "bid_ask_spread": market_structure.get("order_flow", {}).get("spread", 0),
                "depth_imbalance": abs(1 - market_structure.get("order_flow", {}).get("bid_ask_imbalance", 1)),
            },
            "derivatives_risk": {
                "leverage_ratio": market_structure.get("derivatives", {}).get("long_short_ratio", {}).get("global", 1),
                "open_interest_change": market_structure.get("derivatives", {}).get("open_interest_change", 0),
            },
        }

    async def _debug_all_metrics(self, symbol: str, data: dict):
        """Debug output for all collected metrics"""
        logger.debug(f"\n=== Complete Analysis for {symbol} ===")

        # Price and volume metrics
        if "candles" in data:
            logger.debug("\nPrice Metrics:")
            latest_candle = data["candles"][-1]
            logger.debug(f"Current Price: ${latest_candle['close']:.2f}")
            logger.debug(f"24h Volume: ${sum(c['volume'] for c in data['candles'][-24:]):.2f}")

        # Support/Resistance levels
        if "sr_levels" in data:
            logger.debug("\nKey Levels:")
            for level_type in ["support", "resistance"]:
                logger.debug(f"\n{level_type.capitalize()}:")
                for level in data["sr_levels"][level_type]:
                    logger.debug(f"- ${level['price']:.2f} (Significance: {level['significance']:.2f})")

        # Order book analysis
        if "order_book" in data:
            logger.debug("\nOrder Book Analysis:")
            logger.debug(f"Bid/Ask Spread: {data['order_book']['bid_ask_spread']:.4f}%")
            logger.debug(f"Market Depth Ratio: {data['order_book']['depth_ratio']:.4f}")

        # Whale activity
        if "whale_data" in data:
            logger.debug("\nWhale Activity:")
            logger.debug(f"Buy/Sell Ratio: {data['whale_data']['buy_sell_ratio']:.2f}")
            logger.debug(f"Large Trades: {len(data['whale_data']['recent_trades'])}")

        # Derivatives data
        if "derivatives" in data:
            logger.debug("\nDerivatives Metrics:")
            logger.debug(f"Open Interest: {data['derivatives']['open_interest']['total']:.2f}")
            logger.debug(f"Long/Short Ratio: {data['derivatives']['long_short_ratio']['global']:.2f}")

        logger.debug("\n=== End of Analysis ===\n")
