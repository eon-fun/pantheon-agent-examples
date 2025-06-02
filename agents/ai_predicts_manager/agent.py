import json
from anthropic import Anthropic
from typing import Dict, List, Optional
from datetime import datetime
import logging
import asyncio
from aiohttp import ClientSession

from infrastructure.configs.config import settings
from simple_ai_agents.ai_predicts_manager.results import AsyncResultsAnalyzer
from technical import TechnicalAnalysis, MarketStructure
from collector import AsyncDataCollector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AsyncAIAnalyzer:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.ta = TechnicalAnalysis()
        self.market_structure = MarketStructure()
        self.system_prompt = """
You are a based crypto trading chad who's been consistently printing money since 2017. Your job is to spot asymmetric opportunities where technicals, whale activity, and market structure align.

Provide your analysis in this exact format (I will parse it as JSON):

{
    "trade_alerts": [
        {
            "symbol": "BTC",
            "type": "LONG/SHORT",
            "entry": "exact price or zone",
            "targets": ["target1", "target2", "target3"],
            "stop": "exact invalidation level",
            "risk_reward": number,
            "thesis": "Ultra clear reasoning in CT style",
            "risk_level": "COZY/DEGEN/ULTRA DEGEN"
        }
    ],
    "market_alpha": {
        "structure": "Overall market structure analysis",
        "smart_money": "What smart money is doing",
        "retail": "What ngmi retail is doing wrong",
        "whale_activity": "Notable whale/institutional moves",
        "key_levels": {
            "BTC": {
                "support": ["level1", "level2"],
                "resistance": ["level1", "level2"]
            }
        },
        "extra_alpha": ["Additional based insights", "More alpha"]
    }
}

Don't force trades if there are no clear setups. Stay based and back everything with data.
"""

    async def _parse_claude_response(self, response: str) -> Dict:
        """Parse Claude's response with improved error handling"""
        try:
            start = response.find('{')
            end = response.rfind('}')

            if start == -1 or end == -1:
                raise ValueError("No JSON object found in response")

            json_str = response[start:end + 1]
            json_str = json_str.replace('```json', '').replace('```', '')
            parsed = json.loads(json_str)

            if 'trade_alerts' not in parsed or 'market_alpha' not in parsed:
                raise ValueError("Missing required top-level fields")

            if not isinstance(parsed['trade_alerts'], list):
                raise ValueError("trade_alerts must be an array")

            for signal in parsed['trade_alerts']:
                required = ['symbol', 'type', 'entry', 'targets', 'stop',
                            'risk_reward', 'thesis', 'risk_level']
                missing = [field for field in required if field not in signal]
                if missing:
                    raise ValueError(f"Trading alert missing required fields: {missing}")

            required_analysis = ['structure', 'smart_money', 'retail',
                                 'whale_activity', 'key_levels', 'extra_alpha']
            missing = [field for field in required_analysis if field not in parsed['market_alpha']]
            if missing:
                raise ValueError(f"Market analysis missing required fields: {missing}")

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return await self._create_error_response(f"Invalid JSON format: {str(e)}")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return await self._create_error_response(f"Validation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            return await self._create_error_response(f"Unexpected error: {str(e)}")

    async def _format_data_for_analysis(self, market_data: List[Dict]) -> str:
        """Format market data including all technical analysis"""
        formatted = {
            'timestamp': datetime.now().isoformat(),
            'market_data': []
        }

        for coin_data in market_data:
            if not coin_data:
                continue

            timeframes = {}
            for tf in ['1h', '4h', '1d']:
                if coin_data['data'].get(tf):
                    candles = coin_data['data'][tf]

                    # Extract OHLCV data
                    closes = [c['close'] for c in candles]
                    highs = [c['high'] for c in candles]
                    lows = [c['low'] for c in candles]
                    volumes = [c['volume'] for c in candles]

                    # Calculate all technical indicators asynchronously
                    indicators_tasks = [
                        self.ta.calculate_rsi(closes),
                        self.ta.calculate_macd(closes),
                        self.ta.calculate_bollinger_bands(closes),
                        self.ta.calculate_atr(highs, lows, closes),
                        self.ta.calculate_stochastic(highs, lows, closes),
                        self.ta.calculate_obv(closes, volumes),
                        self.ta.calculate_ichimoku(highs, lows)
                    ]

                    rsi, (macd, signal, hist), (bb_upper, bb_middle, bb_lower), atr, \
                    (stoch_k, stoch_d), obv, ichimoku = await asyncio.gather(*indicators_tasks)

                    # Calculate additional indicators and analysis concurrently
                    additional_tasks = [
                        self.ta.detect_divergence(closes, rsi),
                        self.ta.detect_divergence(closes, macd),
                        self.ta.calculate_pivot_points(highs[-1], lows[-1], closes[-1]),
                        self.market_structure.identify_swing_points(highs, lows),
                        self.market_structure.analyze_volume_profile(closes[-100:], volumes[-100:])
                    ]

                    rsi_div, macd_div, pivots, swing_points, volume_profile = await asyncio.gather(*additional_tasks)

                    timeframes[tf] = {
                        'price_data': {
                            'current': closes[-1],
                            'volume_24h': sum(volumes[-24:])
                        },
                        'indicators': {
                            'rsi': {
                                'current': rsi[-1],
                                'history': rsi[-10:],
                                'divergence': rsi_div
                            },
                            'macd': {
                                'current': {
                                    'macd': macd[-1],
                                    'signal': signal[-1],
                                    'histogram': hist[-1]
                                },
                                'history': list(zip(macd[-10:], signal[-10:], hist[-10:])),
                                'divergence': macd_div
                            },
                            'bollinger': {
                                'current': {
                                    'upper': bb_upper[-1],
                                    'middle': bb_middle[-1],
                                    'lower': bb_lower[-1]
                                },
                                'width': (bb_upper[-1] - bb_lower[-1]) / bb_middle[-1]
                            },
                            'atr': {
                                'current': atr[-1],
                                'history': atr[-10:]
                            },
                            'stochastic': {
                                'current': {
                                    'k': stoch_k[-1],
                                    'd': stoch_d[-1]
                                },
                                'history': list(zip(stoch_k[-10:], stoch_d[-10:]))
                            },
                            'obv': {
                                'current': obv[-1],
                                'momentum': (obv[-1] - obv[-20]) / obv[-20] if len(obv) >= 20 else 0
                            }
                        },
                        'market_structure': {
                            'pivot_points': pivots,
                            'ichimoku': {
                                'current': {
                                    key: values[-1] for key, values in ichimoku.items()
                                }
                            },
                            'swing_points': {
                                'recent_highs': swing_points['highs'][-3:],
                                'recent_lows': swing_points['lows'][-3:]
                            },
                            'volume_profile': volume_profile
                        }
                    }

            # Format order flow data
            order_flow = {
                'order_book': coin_data['order_book'] if coin_data['order_book'] else {},
                'whale_activity': coin_data['whale_data'] if coin_data['whale_data'] else {},
                'derivatives': coin_data['derivatives'] if coin_data['derivatives'] else {}
            }

            formatted_coin = {
                'symbol': coin_data['symbol'],
                'timeframes': timeframes,
                'order_flow': order_flow,
                'support_resistance': coin_data['sr_levels']
            }

            formatted['market_data'].append(formatted_coin)

        return json.dumps(formatted, indent=2, default=str)

    async def analyze_data(self, market_data: List[Dict]) -> str:
        """Analyze market data and return CT-style string output"""
        try:
            formatted_data = await self._format_data_for_analysis(market_data)
            prompt = await self._create_analysis_prompt(formatted_data)

            response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

            response_text = response.content[0].text
            parsed_response = await self._parse_json_response(response_text)
            return await self._format_ct_style_output(parsed_response)

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return "⚠️ Analysis Error ⚠️\n\nFailed to generate alpha. Touch grass and try again later."

    async def _create_analysis_prompt(self, formatted_data: str) -> str:
        """Create analysis prompt"""
        return f"""
Analyze this market data and give me the highest conviction plays only:
{formatted_data}

- Only flag the most obvious setups
- Skip any cope or hopium trades
- Tell me what smart money is actually doing
- Point out what ngmi retail is doing wrong
- Include key whale moves and institutional activity

Remember:
1. Be ultra clear about entries, targets, and invalidation
2. Only include trades you'd take yourself
3. Write in based CT style
4. Return response in the exact JSON format specified
"""

    async def _parse_json_response(self, response: str) -> Dict:
        """Extract and parse JSON from Claude's response"""
        try:
            start = response.find('{')
            end = response.rfind('}')

            if start == -1 or end == -1:
                raise ValueError("No JSON found in response")

            json_str = response[start:end + 1].strip()
            return json.loads(json_str)

        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            raise

    async def _create_error_response(self, error_msg: str) -> Dict:
        """Create a standardized error response"""
        return {
            'trading_signals': [],
            'market_analysis': {
                'error': error_msg,
                'market_structure': 'Error analyzing market structure',
                'key_levels': {},
                'smart_money': 'Error analyzing smart money positions',
                'ngmi_retail': 'Error analyzing retail activity',
                'potential_setups': [],
                'whale_moves': 'Error analyzing whale activity',
                'additional_alpha': []
            }
        }

    async def _format_ct_style_output(self, data: Dict) -> str:
        """Format JSON data into CT-style string output"""
        output = []

        # Format trade alerts
        if data.get('trade_alerts'):
            output.append("🚨 TRADE ALERTS 🚨")
            for alert in data['trade_alerts']:
                trade = [
                    f"${alert['symbol']} - {alert['type']}",
                    f"Entry zone: {alert['entry']}",
                    f"Targets: {', '.join(alert['targets'])}",
                    f"Stop: {alert['stop']} = rekt",
                    f"R/R: {alert['risk_reward']}x",
                    f"THESIS: {alert['thesis']}",
                    f"Risk Level: {alert['risk_level']}"
                ]
                output.append('\n'.join(trade))
        else:
            output.append("No clear setups rn anon, don't force trades")

        # Format market alpha
        alpha = data.get('market_alpha', {})
        output.append("\n🧠 MARKET ALPHA 🧠")

        if alpha.get('structure'):
            output.append(alpha['structure'])

        if alpha.get('smart_money'):
            output.append(f"Smart Money:\n- {alpha['smart_money']}")

        if alpha.get('retail'):
            output.append(f"NGMI Retail:\n- {alpha['retail']}")

        if alpha.get('whale_activity'):
            output.append(f"Whale Moves:\n- {alpha['whale_activity']}")

        # Format key levels
        if alpha.get('key_levels'):
            output.append("\nKey Levels:")
            for symbol, levels in alpha['key_levels'].items():
                supports = ', '.join(levels.get('support', []))
                resistances = ', '.join(levels.get('resistance', []))
                output.append(f"${symbol}:")
                if supports:
                    output.append(f"Support: {supports}")
                if resistances:
                    output.append(f"Resistance: {resistances}")

        if alpha.get('extra_alpha'):
            output.append("\nExtra Alpha:")
            output.extend(f"- {alpha}" for alpha in alpha['extra_alpha'])

        return '\n\n'.join(output)

    async def integrate_analysis(self, candles: List[Dict], order_book: Optional[Dict] = None) -> Dict:
        """Integrate all technical analysis and market structure analysis"""
        if not candles:
            return {}

        # Extract price and volume data
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        volumes = [c['volume'] for c in candles]

        # Calculate all metrics concurrently
        tasks = [
            self.ta.calculate_rsi(closes),
            self.ta.calculate_macd(closes),
            self.ta.calculate_bollinger_bands(closes),
            self.ta.calculate_atr(highs, lows, closes),
            self.ta.calculate_stochastic(highs, lows, closes),
            self.ta.calculate_obv(closes, volumes),
            self.ta.calculate_vwap(candles),
            self.ta.calculate_pivot_points(highs[-1], lows[-1], closes[-1]),
            self.ta.calculate_ichimoku(highs, lows),
            self.market_structure.identify_swing_points(highs, lows),
            self.market_structure.analyze_volume_profile(closes[-100:], volumes[-100:])
        ]

        results = await asyncio.gather(*tasks)

        rsi = results[0]
        macd, signal, hist = results[1]
        bb_upper, bb_middle, bb_lower = results[2]
        atr = results[3]
        stoch_k, stoch_d = results[4]
        obv = results[5]
        vwap = results[6]
        pivots = results[7]
        ichimoku = results[8]
        swing_points = results[9]
        volume_profile = results[10]

        # Detect divergences concurrently
        div_tasks = [
            self.ta.detect_divergence(closes, rsi),
            self.ta.detect_divergence(closes, macd)
        ]
        rsi_div, macd_div = await asyncio.gather(*div_tasks)

        return {
            'indicators': {
                'rsi': {
                    'current': rsi[-1],
                    'history': rsi[-10:],
                    'divergence': rsi_div
                },
                'macd': {
                    'current': {
                        'macd': macd[-1],
                        'signal': signal[-1],
                        'histogram': hist[-1]
                    },
                    'history': list(zip(macd[-10:], signal[-10:], hist[-10:])),
                    'divergence': macd_div
                },
                'bollinger_bands': {
                    'current': {
                        'upper': bb_upper[-1],
                        'middle': bb_middle[-1],
                        'lower': bb_lower[-1]
                    },
                    'width': (bb_upper[-1] - bb_lower[-1]) / bb_middle[-1]
                },
                'atr': {
                    'current': atr[-1],
                    'history': atr[-10:]
                },
                'stochastic': {
                    'current': {
                        'k': stoch_k[-1],
                        'd': stoch_d[-1]
                    },
                    'history': list(zip(stoch_k[-10:], stoch_d[-10:]))
                },
                'obv': {
                    'current': obv[-1],
                    'momentum': (obv[-1] - obv[-20]) / obv[-20] if len(obv) >= 20 else 0
                },
                'vwap': {
                    'current': vwap[-1],
                    'history': vwap[-10:],
                    'cross_price': vwap[-1] > closes[-1]
                }
            },
            'market_structure': {
                'pivot_points': pivots,
                'ichimoku': {
                    'current': {
                        key: values[-1] for key, values in ichimoku.items()
                    }
                },
                'swing_points': {
                    'recent_highs': swing_points['highs'][-3:],
                    'recent_lows': swing_points['lows'][-3:]
                },
                'volume_profile': volume_profile
            }
        }


class AsyncCryptoAISystem:
    def __init__(self, anthropic_api_key: str):
        self.data_collector = AsyncDataCollector()
        self.ai_analyzer = AsyncAIAnalyzer(anthropic_api_key)
        self.logger = logging.getLogger(__name__)

    async def run_analysis(self, num_coins: int = 5) -> Dict:
        """Run complete market analysis in continuous mode"""
        # Create results analyzer instance once
        results_analyzer = AsyncResultsAnalyzer()

        while True:
            try:
                async with self.data_collector:
                    # Get top coins
                    logger.info(f"Fetching top {num_coins} coins...")
                    coins = await self.data_collector.get_top_coins(num_coins)

                    if not coins:
                        raise ValueError("Failed to fetch top coins")

                    logger.info(f"Retrieved coins: {[coin['symbol'].upper() for coin in coins]}")

                    # Collect data for each coin
                    market_data = []
                    tasks = [self._collect_coin_data(coin['symbol'].upper()) for coin in coins]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in results:
                        if isinstance(result, Exception):
                            logger.error(f"Error collecting data: {str(result)}")
                        elif result:
                            market_data.append(result)

                    if not market_data:
                        raise ValueError("No valid market data collected")

                    # Run AI analysis
                    logger.info("Running AI analysis...")

                    # Get Claude's analysis
                    analysis = await self.ai_analyzer.analyze_data(market_data)

                    # Process results and save to Redis
                    results = await results_analyzer.process_and_save_signals(market_data, analysis)

                    # Format and log the results
                    output = await results_analyzer.format_output(results)
                    print(output)

                    # Wait before next iteration (5 minutes by default)
                    wait_time = 1800  # 300 seconds = 5 minutes
                    logger.info(f"Waiting {wait_time} seconds until next analysis...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Error in analysis run: {str(e)}")
                # Wait a minute before retrying after error
                await asyncio.sleep(60)

    async def _collect_coin_data(self, symbol: str) -> Optional[Dict]:
        """Collect comprehensive data for a single coin with validation"""
        try:
            # Collect data concurrently
            candle_tasks = {
                '1h': self.data_collector.get_candle_data(symbol, '1h'),
                '4h': self.data_collector.get_candle_data(symbol, '4h'),
                '1d': self.data_collector.get_candle_data(symbol, '1d')
            }

            additional_tasks = {
                'order_book': self.data_collector.get_order_book(symbol),
                'whale_data': self.data_collector.get_whale_data(symbol),
                'derivatives': self.data_collector.get_derivatives_data(symbol)
            }

            # Gather all data concurrently
            candle_results = await asyncio.gather(*candle_tasks.values(), return_exceptions=True)
            additional_results = await asyncio.gather(*additional_tasks.values(), return_exceptions=True)

            # Process candle data
            candle_data = {}
            for tf, result in zip(candle_tasks.keys(), candle_results):
                if isinstance(result, Exception):
                    self.logger.warning(f"Error fetching {tf} candles for {symbol}: {str(result)}")
                    return None
                candle_data[tf] = result

            # Verify we have valid candle data
            if not all(candle_data.values()):
                self.logger.warning(f"Missing candle data for {symbol}")
                return None

            # Process additional data
            order_book, whale_data, derivatives = additional_results

            # Calculate S/R levels for each timeframe
            sr_levels = {}
            for timeframe, candles in candle_data.items():
                sr_levels[timeframe] = await self.data_collector._calculate_sr_levels(candles)
                await self.data_collector._debug_sr_levels(symbol, timeframe, sr_levels[timeframe])

            # Validate all collected data
            order_book = await self.data_collector._validate_order_book(order_book)
            whale_data = await self.data_collector._validate_whale_data(whale_data)

            # Debug output
            await self.data_collector._debug_order_book(symbol, order_book)
            await self.data_collector._debug_whale_data(symbol, whale_data)

            return {
                'symbol': symbol,
                'data': candle_data,
                'sr_levels': sr_levels,
                'order_book': order_book,
                'whale_data': whale_data,
                'derivatives': derivatives
            }

        except Exception as e:
            self.logger.error(f"Error collecting data for {symbol}: {str(e)}")
            return None

    async def _create_error_response(self, error_msg: str) -> Dict:
        """Create a standardized error response"""
        return {
            'trading_signals': [],
            'market_analysis': {
                'error': error_msg,
                'market_structure': 'Error analyzing market structure',
                'key_levels': {},
                'smart_money': 'Error analyzing smart money positions',
                'ngmi_retail': 'Error analyzing retail activity',
                'potential_setups': [],
                'whale_moves': 'Error analyzing whale activity',
                'additional_alpha': []
            }
        }

    async def _calculate_risk_metrics(self, timeframes: Dict, market_structure: Dict) -> Dict:
        """Calculate comprehensive risk metrics"""
        # Use 1h timeframe for recent volatility
        hourly_data = timeframes.get('1h', {}).get('technical_analysis', {})

        return {
            'volatility_risk': {
                'current_atr': hourly_data.get('indicators', {}).get('atr', {}).get('current', 0),
                'bb_width': hourly_data.get('indicators', {}).get('bollinger_bands', {}).get('width', 0)
            },
            'momentum_risk': {
                'rsi_extreme': abs(50 - hourly_data.get('indicators', {}).get('rsi', {}).get('current', 50)),
                'macd_histogram': hourly_data.get('indicators', {}).get('macd', {}).get('current', {}).get(
                    'histogram', 0)
            },
            'liquidity_risk': {
                'bid_ask_spread': market_structure['order_flow']['spread'],
                'depth_imbalance': abs(1 - market_structure['order_flow']['bid_ask_imbalance'])
            },
            'derivatives_risk': {
                'leverage_ratio': market_structure['derivatives']['long_short_ratio'],
                'open_interest_change': 0  # Would need historical data to calculate change
            }
        }

    async def _debug_print_data(self, data: Dict):
        """Print detailed debug information about collected data"""
        try:
            print(f"\nData collected for {data['symbol']}:")

            # Print candle data summary
            for timeframe, candles in data['data'].items():
                if candles:
                    print(f"- {timeframe} candles: {len(candles)} periods")
                    print(f"  Latest price: {candles[-1]['close']:.2f}")
                    print(f"  24h volume: {sum(c['volume'] for c in candles[-24:]):.2f}")

            # Print S/R levels
            print("\nSupport/Resistance Levels:")
            for timeframe, levels in data['sr_levels'].items():
                print(f"\n{timeframe} timeframe:")
                for level_type in ['support', 'resistance']:
                    print(f"{level_type.capitalize()} levels:")
                    for level in levels[level_type]:
                        print(f"  Price: {level['price']:.2f}, Touches: {level['touches']}, "
                              f"Significance: {level['significance']:.2f}")

            # Print order book summary
            if data['order_book']:
                print("\nOrder Book:")
                print(f"- Bid/Ask Spread: {data['order_book']['bid_ask_spread']:.2f}%")
                print(f"- Depth Ratio: {data['order_book'].get('depth_ratio', 'N/A')}")

            # Print whale data
            if data['whale_data']:
                print("\nWhale Activity:")
                print(f"- Recent trades: {len(data['whale_data']['recent_trades'])}")
                print(f"- Buy/Sell ratio: {data['whale_data']['buy_sell_ratio']:.2f}")

            # Print derivatives data
            if data['derivatives']:
                print("\nDerivatives Data:")
                print(f"- Open Interest: {data['derivatives']['open_interest']['total']:.2f}")
                print(f"- Long/Short Ratio: {data['derivatives']['long_short_ratio']['global']:.2f}")

        except Exception as e:
            self.logger.error(f"Error in debug printing: {str(e)}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create system instance
    system = AsyncCryptoAISystem(settings.ANTHROPIC_API_KEY)

    # Run the analysis loop
    asyncio.run(system.run_analysis(num_coins=5))
