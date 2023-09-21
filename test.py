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

# Connect to the API and fetch balance and open positions
load_dotenv(dotenv_path=r'C:\Users\wangr\PycharmProjects\pythonProject9\config\api.keys.env')
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

connected_api = ConnectedAPI(api_key, secret_key)
balances, output_data = connected_api.get_account_balance()
positions, output_data = connected_api.get_open_positions()

# Define the table name
table_name = "traiding_bot_binance"

    # Log the balances and positions
logger.info("Balances:")
for asset, balance in balances:
    logger.info("Currency: %s, Balance: %s", asset, balance)

if positions:
    logger.info("Open Positions:")
    for symbol, position_side, position_amt in positions:
        logger.info("Symbol: %s, Position Side: %s, Position Amount: %s", symbol, position_side, position_amt)
else:
    logger.info("No open positions.")

def fetch_and_store_historical_data():
    # Use default settings from DefaultConfig
    fetcher = HistoricalPriceFetcher()
    historical_candle_data = fetcher.fetch_historical_data()

    if historical_candle_data:
        # Store historical data in the database
        db_manager = DatabaseManager()
        db_manager.insert_data(historical_candle_data)
        db_manager.close_connection()

# Call the function to fetch and store historical data
fetch_and_store_historical_data()

def fetch_historical_data_for_chart():
    db_manager = DatabaseManager()
    chart_data = db_manager.fetch_data_for_chart()
    db_manager.close_connection()
    return chart_data

def plot_candlestick_chart():
    # Create an instance of CandlestickChart and pass the logger
    chart = CandlestickChart()
    chart.plot_chart()

    # Close the database connection
    db_manager = DatabaseManager()
    db_manager.close_connection()

# Call the function to plot the candlestick chart
plot_candlestick_chart()

def fetch_historical_data_for_chart():
    db_manager = DatabaseManager()
    chart_data = db_manager.fetch_data_for_chart()
    db_manager.close_connection()
    return chart_data


# Define a function to fetch the latest candle data and perform subsequent actions
def fetch_latest_candle():
    fetcher = HistoricalPriceFetcher()
    fetcher.fetch_latest_candle_data()

    # Fetch historical data for chart
    db_manager = DatabaseManager()
    chart_data = fetch_historical_data_for_chart()
    # Close the database connection
    db_manager.close_connection()


# Call the function to fetch latest candle data and perform subsequent actions
fetch_latest_candle()