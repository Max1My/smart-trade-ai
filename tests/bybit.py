import json
import time
from collections import defaultdict

from pybit.unified_trading import WebSocket

from app.schemas.market import MarketCreateSchema

TOP_20_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT",
    "ADAUSDT", "DOGEUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT",
    "AVAXUSDT", "LINKUSDT", "ATOMUSDT", "XMRUSDT",
    "ETCUSDT", "BCHUSDT", "NEARUSDT", "APTUSDT", "FILUSDT"
]


class Bybit:

    def __init__(self):
        self.buffer = defaultdict(list)
        self.last_flush_time = time.monotonic()

    def handle_message(self, message):
        print("Получены данные:", message)

    def add_to_buffer(self, message):
        symbol = message["topic"].split(".")[-1]
        self.buffer[symbol].append(message)

    def flush_buffer(self):
        payloads: list[MarketCreateSchema] = []
        for symbol, messages in self.buffer.items():
            if not messages:
                continue  # Пропускаем пустые списки
            for message in messages:
                if "data" not in message:
                    print(f"⚠ Сообщение без 'data': {message}")
                    continue

                data = message["data"]
                print(f'data: {data}')

                # Обрабатываем список или словарь
                if isinstance(data, list):
                    if not data:  # Пустой список
                        print(f"⚠ Пустой массив данных: {message}")
                        continue
                    processed_data = []
                    for item in data:
                        if isinstance(item, dict):
                            processed_data.append(item)
                        else:
                            print(f"⚠ Не словарь в элементе списка: {item}")

                    # Если необходимо, можно обернуть все данные в общий словарь
                    data = {"data": processed_data}

                elif isinstance(data, dict) and not data:
                    print(f"⚠ Пустой словарь данных: {message}")
                    continue

                payloads.append(MarketCreateSchema(
                    currency=symbol,
                    kind=message["topic"],
                    data=data
                ))
        print(f'payloads: {payloads}')
        self.buffer.clear()
        self.last_flush_time = time.monotonic()  # Обновляем время последнего сброса

    def run(self):

        ws = WebSocket(testnet=False, channel_type="linear")  # Для USDT фьючерсов
        while True:
            try:
                for symbol in TOP_20_SYMBOLS:
                    ws.orderbook_stream(symbol=symbol, callback=self.add_to_buffer, depth=50)
                    ws.kline_stream(symbol=symbol, interval=1, callback=self.add_to_buffer)
                    ws.trade_stream(symbol=symbol, callback=self.add_to_buffer)
                    ws.liquidation_stream(symbol=symbol, callback=self.add_to_buffer)

                print(f"✅ Подписаны  валютных пар")

                while True:
                    time.sleep(1)  # Проверяем раз в секунду

                    if time.monotonic() - self.last_flush_time >= 5:
                        if self.buffer:
                            self.flush_buffer()

            except Exception as e:
                print(f"⚠ Ошибка WebSocket: {e}. Переподключение через 5 секунд...")
            time.sleep(5)

Bybit().run()
print("Тест завершен")
