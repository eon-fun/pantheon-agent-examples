import asyncio
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from database.redis.redis_client import db

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AsyncResultsAnalyzer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    def __del__(self):
        """Cleanup executor on deletion"""
        self.executor.shutdown(wait=False)

    async def debug_signal_storage(self, symbol: str, direction: str):
        """Отладочная функция для проверки состояния сигналов в Redis"""
        try:
            # Получаем все сигналы для данного символа
            signals = db.r.zrangebyscore("trading_signals", "-inf", "+inf", withscores=True)

            matching_signals = [
                (s.decode("utf-8"), score)
                for s, score in signals
                if s.decode("utf-8").startswith(f"{symbol}:{direction}")
            ]

            logger.info(f"Current signals for {symbol}:{direction}:")
            for signal, score in matching_signals:
                logger.info(f"  - {signal} at {datetime.fromtimestamp(int(score))}")

            return len(matching_signals)

        except Exception as e:
            logger.error(f"Error checking signals: {str(e)}")
            return 0

    async def process_and_save_signals(self, market_data: list[dict], claude_analysis: str) -> dict[str, dict]:
        """Обработка данных и сохранение сигналов с отладкой"""
        try:
            simplified_results = {}
            current_timestamp = int(time.time())

            # Парсим данные от Claude
            claude_data = await self._parse_claude_analysis(claude_analysis)
            logger.info(f"Parsed Claude data: {claude_data}")

            # Обрабатываем каждую монету
            tasks = []
            for coin_data in market_data:
                symbol = coin_data.get("symbol", "")
                if not symbol:
                    continue

                coin_claude_data = claude_data.get(symbol, {})
                logger.info(f"Processing {symbol} with Claude data: {coin_claude_data}")

                task = asyncio.create_task(self._process_coin_data(coin_data, coin_claude_data))
                tasks.append((symbol, task))

            # Собираем результаты с сохранением порядка
            for symbol, task in tasks:
                try:
                    symbol, direction, confidence, reasons = await task

                    # Проверяем текущее состояние сигналов
                    current_signals = await self.debug_signal_storage(symbol, direction)
                    logger.info(f"Current signals count for {symbol}:{direction}: {current_signals}")

                    # Сохраняем результат
                    simplified_results[symbol] = {
                        "predicted_direction": direction,
                        "confidence": confidence,
                        "key_reasons": reasons,
                        "timestamp": current_timestamp,
                    }

                    # Сохраняем в Redis с обработкой ошибок
                    try:
                        await self._save_signal_to_redis(symbol, direction, confidence, reasons, current_timestamp)
                        logger.info(f"Successfully saved signal to Redis: {symbol}:{direction}")

                        # Проверяем, что сигнал действительно сохранился
                        new_signals = await self.debug_signal_storage(symbol, direction)
                        logger.info(f"Updated signals count for {symbol}:{direction}: {new_signals}")

                    except Exception as redis_error:
                        logger.error(f"Failed to save signal to Redis for {symbol}: {str(redis_error)}")

                except Exception as e:
                    logger.error(f"Error processing results for {symbol}: {str(e)}")
                    continue

            return simplified_results

        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            return {}

    async def _save_signal_to_redis(
        self, symbol: str, direction: str, confidence: float, reasons: list[str], timestamp: int = None
    ):
        """Сохранение сигнала в Redis с уникальным идентификатором"""
        if timestamp is None:
            timestamp = int(time.time())

        try:
            # Создаем уникальный timestamp с миллисекундами
            unique_timestamp = timestamp + (time.time_ns() % 1000) / 1000.0

            # Создаем уникальный ключ, включающий время
            signal_key = f"{symbol}:{direction}:{unique_timestamp}"

            # Сохраняем в сортированном множестве
            db.add_to_sorted_set("trading_signals", unique_timestamp, signal_key)

            logger.info(f"Successfully saved signal to Redis: {signal_key} at {unique_timestamp}")

        except Exception as e:
            logger.error(f"Failed to save signal to Redis for {symbol}: {str(e)}")
            raise

    async def _parse_claude_analysis(self, claude_analysis: str) -> dict[str, dict]:
        """Парсит анализ от Claude"""
        try:
            signals = {}

            # Парсим торговые сигналы
            if "TRADE ALERTS" in claude_analysis:
                alerts_text = claude_analysis.split("TRADE ALERTS")[1].split("MARKET ALPHA")[0]

                # Ищем сигналы для каждой монеты
                for symbol in ["BTC", "ETH"]:
                    if f"${symbol}" in alerts_text:
                        alert_lines = [line.strip() for line in alerts_text.split("\n") if line.strip()]
                        for i, line in enumerate(alert_lines):
                            if f"${symbol}" in line:
                                direction = "LONG" if "LONG" in line else "SHORT"
                                thesis = ""
                                risk_level = ""

                                for next_line in alert_lines[i:]:
                                    if "THESIS:" in next_line:
                                        thesis = next_line.split("THESIS:")[1].strip()
                                    if "Risk Level:" in next_line:
                                        risk_level = next_line.split("Risk Level:")[1].strip()

                                signals[symbol] = {
                                    "type": direction,
                                    "thesis": thesis,
                                    "risk_level": risk_level,
                                    "direction": "UP" if direction == "LONG" else "DOWN",
                                }

            # Парсим общий анализ рынка
            market_data = {}
            if "MARKET ALPHA" in claude_analysis:
                market_text = claude_analysis.split("MARKET ALPHA")[1]
                market_lines = [line.strip() for line in market_text.split("\n") if line.strip()]

                for line in market_lines:
                    if line and not line.startswith("🧠"):
                        if not market_data.get("structure"):
                            market_data["structure"] = line
                        elif "smart money" in line.lower():
                            market_data["smart_money"] = line
                        elif "whale" in line.lower():
                            market_data["whale_activity"] = line

            signals["market_sentiment"] = market_data
            return signals

        except Exception as e:
            logger.error(f"Error parsing Claude analysis: {e}")
            return {}

    async def _process_coin_data(self, coin_data: dict, claude_data: dict) -> tuple[str, str, float, list[str]]:
        """Обработка данных одной монеты"""
        try:
            symbol = coin_data.get("symbol", "UNKNOWN")
            logger.info(f"Processing {symbol} with Claude data: {claude_data}")

            # Получаем технические сигналы
            technical_signals = await self._collect_signals(coin_data)

            # Определяем направление и уверенность
            direction, confidence, tech_reasons = await self._determine_direction(technical_signals, claude_data)

            # Формируем список причин
            reasons = []

            # Всегда добавляем тезис Claude первым, если он есть
            if claude_data and isinstance(claude_data, dict):
                if claude_data.get("thesis"):
                    reasons.append(f"Claude: {claude_data['thesis'][:200]}...")

            # Добавляем технические причины
            if tech_reasons:
                reasons.extend(tech_reasons)

            # Если список пустой, добавляем базовое объяснение
            if not reasons:
                reasons = ["Базовый технический анализ"]

            logger.info(f"Final reasons for {symbol}: {reasons}")
            return symbol, direction, confidence, reasons[:3]

        except Exception as e:
            logger.error(f"Error processing coin data for {symbol}: {e}")
            return symbol, "NEUTRAL", 0.51, ["Ошибка обработки данных"]

    async def _collect_signals(self, coin_data: dict) -> dict[str, float]:
        """Собирает все сигналы"""
        try:
            signals = {}
            data = coin_data.get("data", {})

            # Анализ временных интервалов
            timeframe_tasks = []
            for timeframe in ["1h", "4h", "1d"]:
                if timeframe in data and data[timeframe]:
                    task = asyncio.create_task(self._analyze_timeframe(timeframe, data[timeframe]))
                    timeframe_tasks.append(task)

            # Выполняем все задачи
            results = await asyncio.gather(*timeframe_tasks)
            for result in results:
                signals.update(result)

            # Анализ китов
            whale_data = coin_data.get("whale_data", {})
            if whale_data:
                buy_sell_ratio = whale_data.get("buy_sell_ratio", 1.0)
                signals["whale_activity"] = 1.0 if buy_sell_ratio > 1.2 else (-1.0 if buy_sell_ratio < 0.8 else 0.0)

            return signals

        except Exception as e:
            logger.error(f"Error collecting signals: {e}")
            return {}

    async def _analyze_timeframe(self, timeframe: str, candles: list[dict]) -> dict[str, float]:
        """Асинхронный анализ временного интервала"""
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self._calculate_timeframe_signals, timeframe, candles
        )

    def _calculate_timeframe_signals(self, timeframe: str, candles: list[dict]) -> dict[str, float]:
        """Расчет сигналов для временного интервала"""
        try:
            if not candles or len(candles) < 2:
                return {}

            signals = {}
            closes = [float(c["close"]) for c in candles]
            volumes = [float(c["volume"]) for c in candles]
            highs = [float(c["high"]) for c in candles]
            lows = [float(c["low"]) for c in candles]

            # Моментум на основе нескольких факторов
            recent_momentum = (closes[-1] - closes[-2]) / closes[-2]
            price_range = (highs[-1] - lows[-1]) / closes[-1]
            volume_change = (volumes[-1] - volumes[-2]) / volumes[-2]

            momentum = recent_momentum * 0.5 + price_range * 0.3 + volume_change * 0.2
            signals[f"momentum_{timeframe}"] = 1.0 if momentum > 0 else -1.0

            # Объемный тренд
            if len(volumes) >= 5:
                avg_volume = sum(volumes[-5:]) / 5
                volume_trend = (volumes[-1] - avg_volume) / avg_volume
                signals[f"volume_{timeframe}"] = 1.0 if volume_trend > 0 else -1.0

            # Тренд цены
            if len(closes) >= 20:
                sma20 = sum(closes[-20:]) / 20
                volatility = sum(abs(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(-20, -1)) / 19
                trend_strength = (closes[-1] - sma20) / (sma20 * volatility)
                signals[f"trend_{timeframe}"] = 1.0 if trend_strength > 0 else -1.0

            return signals

        except Exception as e:
            logger.error(f"Error calculating timeframe signals: {e}")
            return {}

    async def _determine_direction(
        self, technical_signals: dict[str, float], claude_data: dict
    ) -> tuple[str, float, list[str]]:
        """Определение направления движения с улучшенной обработкой сигналов"""
        try:
            total_score = 0
            total_weight = 0
            signals_weight = []
            reasons = []

            # Базовые веса для разных типов сигналов
            base_weights = {
                "momentum_1h": 1.0,
                "momentum_4h": 0.8,
                "momentum_1d": 0.6,
                "trend_1h": 0.8,
                "trend_4h": 0.9,
                "trend_1d": 1.0,
                "volume_1h": 0.7,
                "volume_4h": 0.6,
                "volume_1d": 0.5,
                "whale_activity": 1.2,
            }

            # Обработка технических сигналов
            for signal_name, signal_value in technical_signals.items():
                if abs(signal_value) < 0.1:  # Игнорируем слишком слабые сигналы
                    continue

                base_weight = base_weights.get(signal_name, 1.0)
                # Добавляем контролируемую случайность к весам
                weight = base_weight * (1.0 + (random.random() - 0.5) * 0.1)
                importance = abs(signal_value * weight)

                if abs(signal_value) >= 0.5:
                    direction_text = "бычий" if signal_value > 0 else "медвежий"
                    signal_strength = "сильный" if abs(signal_value) > 0.8 else "умеренный"
                    signals_weight.append((importance, f"{signal_name}: {signal_strength} {direction_text} сигнал"))

                total_score += signal_value * weight
                total_weight += weight

            # Учитываем сигнал от Claude
            if claude_data.get("type"):
                claude_weight = 1.5
                claude_signal = 1.0 if claude_data["type"] == "LONG" else -1.0
                rand_factor = 1.0 + (random.random() - 0.5) * 0.1  # ±5% случайности
                total_score += claude_signal * claude_weight * rand_factor
                total_weight += claude_weight

            # Если нет сигналов
            if total_weight == 0:
                return "UP", 0.51, []

            # Сортируем и берем самые важные сигналы
            signals_weight.sort(reverse=True)
            reasons = [reason for _, reason in signals_weight[:2]]

            # Определяем направление и уверенность с небольшой случайностью
            final_score = total_score / total_weight
            confidence_base = 0.5 + min(abs(final_score) / 2, 0.5)
            confidence = min(0.99, max(0.51, confidence_base * (1.0 + (random.random() - 0.5) * 0.06)))

            direction = "UP" if final_score >= 0 else "DOWN"

            return direction, confidence, reasons

        except Exception as e:
            logger.error(f"Error determining direction: {e}")
            return "UP", 0.51, ["Ошибка анализа"]

    async def format_output(self, results: dict[str, dict]) -> str:
        """Форматирование результатов"""
        try:
            output = []
            for symbol, data in results.items():
                direction_emoji = "🟢" if data["predicted_direction"] == "UP" else "🔴"
                confidence_percentage = f"{data['confidence'] * 100:.1f}%"

                summary = [
                    f"{direction_emoji} {symbol}: Следующая свеча {data['predicted_direction']} ({confidence_percentage})",
                    "Обоснование:",
                    *[f"- {reason}" for reason in data["key_reasons"]],
                    "",
                ]
                output.append("\n".join(summary))

            return "\n".join(output)
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
            return "Ошибка форматирования результатов"
