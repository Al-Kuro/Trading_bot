import ccxt
import time
import requests
import telebot
import matplotlib.pyplot as plt
import numpy as np

# Код из ChatGPT
# Настройки API Bybit
API_KEY = 'YOUR_BYBIT_API_KEY'
API_SECRET = 'YOUR_BYBIT_API_SECRET'
exchange = ccxt.bybit({'apiKey': API_KEY, 'secret': API_SECRET})

# Настройки Telegram бота
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Функция для распознавания Bullish Bat паттерна
def is_bullish_bat(pattern_data):
    # Определяем условия Bullish Bat паттерна
    open_1, high_1, low_1, close_1 = pattern_data[0]
    open_2, high_2, low_2, close_2 = pattern_data[1]
    open_3, high_3, low_3, close_3 = pattern_data[2]
    open_4, high_4, low_4, close_4 = pattern_data[3]

    # Проверяем условия паттерна
    condition_1 = close_1 < open_1 and close_2 > open_2
    condition_2 = low_3 < min(open_1, close_1) and low_3 < min(open_2, close_2)
    condition_3 = high_3 > max(open_1, close_1) and high_3 > max(open_2, close_2)
    condition_4 = close_3 > open_3 and close_4 < open_4

    return condition_1 and condition_2 and condition_3 and condition_4


# Функция для получения свечей и определения паттернов
def find_patterns(symbol, timeframe):
    try:
        # Получить последние 200 свечей
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)

        # Преобразовать данные свечей в numpy массив
        ohlcv_np = np.array(ohlcv)

        # Определить паттерн в массиве свечей
        pattern_data = ohlcv_np[-4:]  # Используем последние 4 свечи для определения паттерна

        # Если найден Bullish Bat паттерн, отправить скриншот в Telegram
        if is_bullish_bat(pattern_data):
            plot_pattern(symbol, ohlcv, timeframe)

    except Exception as e:
        print(f"Error finding patterns for {symbol} ({timeframe}): {e}")


# Функция для построения графика свечей и сохранения скриншота
def plot_pattern(symbol, ohlcv, timeframe):
    plt.figure(figsize=(12, 6))
    plt.title(f"{symbol} - Candlestick Chart ({timeframe})")
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.candlestick2_ohlc(plt.gca(), ohlcv[:, 1], ohlcv[:, 2], ohlcv[:, 3], ohlcv[:, 4], width=0.6, colorup='g',
                          colordown='r')

    # Сохранить график как файл
    img_file = f"{symbol}_{timeframe}_chart.png"
    plt.savefig(img_file)

    # Отправить скриншот в Telegram
    send_telegram_message(f"{symbol} - Bullish Bat Pattern Detected ({timeframe})!", img_file)


# Функция для отправки сообщения в Telegram с прикрепленным изображением
def send_telegram_message(message, img_file=None):
    if img_file:
        with open(img_file, 'rb') as photo:
            telegram_bot.send_photo(CHAT_ID, photo)
    else:
        telegram_bot.send_message(CHAT_ID, message)


# Основной цикл для сканирования и поиска паттернов
def main():
    # Загрузить список доступных рынков (торговых пар) с биржи
    markets = exchange.load_markets()

    # Отфильтровать список рынков, оставив только торговые пары с базовой валютой USDT
    symbols = [symbol for symbol in markets.keys() if symbol.endswith('/USDT')]

    # Список таймфреймов, по которым будем проходить
    timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '4h']

    while True:
        try:
            for symbol in symbols:
                for timeframe in timeframes:
                    find_patterns(symbol, timeframe)
                    time.sleep(2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(10)


if __name__ == '__main__':
    CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'  # Укажите ваш chat_id для отправки сообщений
    main()
