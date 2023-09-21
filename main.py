from dotenv import load_dotenv
import os
import time
import datetime
import logging
import sys
from connected_api import ConnectedAPI
from historical_prices import HistoricalPriceFetcher
from database import DatabaseManager
from custom_logger import ColoredConsoleHandler
from grapf_objects import CandlestickChart

# Настройка логирования
logger = logging.getLogger(__name__)  # Инициализация логгера
logger.setLevel(logging.INFO)  # Установка уровня логирования на INFO

# Создание обработчика для вывода в консоль с цветами
handler = ColoredConsoleHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Добавление обработчика к логгеру
logger.addHandler(handler)

def main():
    # Загрузка переменных окружения из файла .env
    load_dotenv(dotenv_path=r'C:\Users\wangr\PycharmProjects\pythonProject9\config\api.keys.env')
    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("SECRET_KEY")

    # Создание экземпляра ConnectedAPI
    connected_api = ConnectedAPI(api_key, secret_key)

    # Вызов метода get_account_balance
    balances, output_data = connected_api.get_account_balance()

    # Вызов метода get_open_positions
    positions, output_data = connected_api.get_open_positions()

    # Логирование балансов и позиций
    logger.info("=====================\nBalances:")
    for asset, balance in balances:
        logger.info("Валюта: %s, Баланс: %s", asset, balance)
        logger.info("=====================")

    # Логирование позиций или их отсутствия
    if positions:
        logger.info("======================\nОткрытые позиции:")
        for symbol, position_side, position_amt in positions:
            logger.info("Symbol: %s, Position Side: %s, Position Amount: %s", symbol, position_side, position_amt)
            logger.info("======================")
    else:
        logger.info("Открытых позиций нет.\n======================")

    # Определение имени таблицы
    table_name = "traiding_bot_binance"

    # Получение исторических данных по инструменту
    fetcher = HistoricalPriceFetcher()
    historical_candle_data = fetcher.fetch_historical_data()

    if historical_candle_data:
        # Логирование успешного получения и количества записей
        logger.info("Количество полученных записей: %s", len(historical_candle_data))

        # Извлечение названий столбцов из биржи
        column_names = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']

        # Вывод последних данных
        latest_candle = historical_candle_data[-1]
        logger.info(' | '.join(column_names))
        logger.info(' | '.join(str(item) for item in latest_candle))

        # Подключение к базе данных и вставка данных
        db_manager = DatabaseManager()
        db_manager.insert_data(table_name, historical_candle_data)

        db_manager.close_connection()
    else:
        logger.error("No historical data received.")

        # Create an instance of DatabaseManager
        db_manager = DatabaseManager()

        # Fetch data for chart
        chart_data = db_manager.fetch_data_for_chart(table_name)

        # Plot the candlestick chart
        chart = CandlestickChart()
        chart.plot_chart(chart_data)

    historical_price_fetcher = HistoricalPriceFetcher()

    # Получение начального времени для сравнения
    initial_timeframe = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)

    while True:
        # Ожидание изменения временного интервала (в данном случае каждый час)
        while datetime.datetime.now().replace(minute=0, second=0, microsecond=0) == initial_timeframe:
            time.sleep(10)  # Подстройте это задержку в зависимости от желаемой частоты проверки

        # Обновление начального временного интервала для следующей итерации
        initial_timeframe = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)

        # Получение последних данных свечи
        latest_candle_data = historical_price_fetcher.fetch_latest_candle_data()

        # Вставка данных последней свечи в базу данных
        if latest_candle_data:
            db_manager = DatabaseManager()
            db_manager.insert_data(table_name, [latest_candle_data])  # Обратите внимание на [latest_candle_data]
            db_manager.close_connection()


if __name__ == "__main__":
    main()
