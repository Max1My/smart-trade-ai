import time
from pybit.unified_trading import WebSocket


def handle_message(message):
    print("Получены данные:", message)


ws = WebSocket(testnet=False, channel_type="linear")  # Для USDT фьючерсов

ws.orderbook_stream(symbol="BTCUSDT", callback=handle_message, depth=50)  # orderbook.50
ws.kline_stream(symbol="BTCUSDT", interval=1, callback=handle_message)  # Свечи 1 минута
ws.trade_stream(symbol="BTCUSDT", callback=handle_message)  # История сделок
ws.liquidation_stream(symbol="BTCUSDT", callback=handle_message)  # Ликвидации

time.sleep(5)  # Собираем данные 30 секунд

print("Тест завершен")
