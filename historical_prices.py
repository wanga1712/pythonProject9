import ccxt
import datetime
import logging
import time
from datetime import datetime, timedelta
from custom_logger import LoggerConfig
from configuration_default import DefaultConfig


class HistoricalPriceFetcher:
    """
    Класс HistoricalPriceFetcher предназначен для получения исторических данных о цене торгуемого инструмента.

    Parameters:
        symbol (str): Символ торгуемого инструмента (по умолчанию: 'BTC/USDT').
        timeframe (str): Временной интервал (по умолчанию: '1h').
        period (int): Количество свечей (по умолчанию: 1500).

    Attributes:
        symbol (str): Символ торгуемого инструмента.
        timeframe (str): Временной интервал.
        period (int): Количество свечей.
        exchange (ccxt.Exchange): Объект обмена данными с биржей.
        logger (logging.Logger): Объект логгера для записи сообщений.

    Methods:
        fetch_historical_data: Получает исторические данные о цене для указанного инструмента и периода.
    """

    def __init__(self, symbol=None, timeframe=None, period=None):
        """
        Инициализация объекта HistoricalPriceFetcher.

        Parameters:
            symbol (str): Символ торгуемого инструмента.
            timeframe (str): Временной интервал.
            period (int): Количество свечей.

        """
        self.configuration_default = DefaultConfig()  # Initialize with default settings
        # Override with provided settings if available
        if symbol:
            self.configuration_default.symbol = symbol
        if timeframe:
            self.configuration_default.timeframe = timeframe
        if period:
            self.configuration_default.period = period

        # Конфигурация логгера
        self.exchange = ccxt.binance()
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

    def some_method(self):
        self.logger.debug('Debug message')
        self.logger.info('Informational message')
        self.logger.warning('Warning message')
        self.logger.error('Error message')
        self.logger.exception('Critical message')


    def fetch_historical_data(self):
        try:
            # Use self.configuration_default.symbol instead of self.symbol
            current_server_time = self.exchange.fetch_ticker(self.configuration_default.symbol)['timestamp']
            timeframe_in_milliseconds = self.exchange.parse_timeframe(self.configuration_default.timeframe) * 1000
            # Рассчет подходящего начального и конечного времени на основе временного интервала и количества периодов
            periods = 1000  # Желаемое количество периодов
            end_time = current_server_time
            start_time = current_server_time - (periods * timeframe_in_milliseconds)

            # Извлечение данных OHLCV
            ohlcv = self.exchange.fetch_ohlcv(self.configuration_default.symbol, timeframe=self.configuration_default.timeframe, since=start_time, limit=1500)
            # Фильтрация данных до указанного конечного времени
            filtered_ohlcv = [candle for candle in ohlcv if candle[0] <= end_time]

            # Переформатирование меток времени для читаемости
            for i in range(len(filtered_ohlcv)):
                filtered_ohlcv[i][0] = datetime.fromtimestamp(filtered_ohlcv[i][0] / 1000.0).strftime(
                    '%Y-%m-%d %H:%M:%S')

            self.logger.debug("Успешно получены исторические ценовые данные.")
            return filtered_ohlcv

        except Exception as e:
            self.logger.error(f"Произошла ошибка при извлечении исторических данных: {str(e)}")
            return []

    def fetch_latest_candle_data(self):
        try:
            while True:
                # Get the current server time in milliseconds
                current_server_time_ms = self.exchange.fetch_ticker(self.configuration_default.symbol)['timestamp']

                # Convert the timestamp to the desired format
                current_server_time = datetime.fromtimestamp(current_server_time_ms / 1000.0).strftime(
                    '%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Calculate the start time for the next hour, plus one minute
                next_hour = (datetime.fromtimestamp(current_server_time_ms / 1000.0)
                             .replace(minute=1, second=0, microsecond=0))  # Set the minute to 1 for the next hour
                if datetime.now().minute >= 1:
                    next_hour = next_hour + timedelta(
                        hours=1)  # Move to the next hour if the current time is past 1 minute

                start_of_next_hour = int(next_hour.timestamp()) * 1000  # Convert to milliseconds

                # Fetch data for the next hour
                data_for_next_hour = self.exchange.fetch_ohlcv(self.configuration_default.symbol,
                                                               timeframe=self.configuration_default.timeframe,
                                                               since=start_of_next_hour, limit=1)

                # Sleep until the start of the next candle
                sleep_time = max(0, (start_of_next_hour - current_server_time_ms) / 1000) + 60  # Add 60 seconds
                time.sleep(sleep_time)

                # Fetch the next upcoming candle
                next_candle_data = self.exchange.fetch_ohlcv(self.configuration_default.symbol,
                                                             timeframe=self.configuration_default.timeframe,
                                                             since=start_of_next_hour,
                                                             limit=1)

                if next_candle_data:
                    latest_candle_data = {
                        'timestamp': current_server_time,
                        'open_price': next_candle_data[0][1],
                        'high_price': next_candle_data[0][2],
                        'low_price': next_candle_data[0][3],
                        'close_price': next_candle_data[0][4],
                        'volume': next_candle_data[0][5]
                    }
                    # Log the fetched candle data and success message
                    self.logger.info("Fetched Latest Candle Data: %s", latest_candle_data)
                    self.logger.info("Successfully fetched the latest candle data.")

                    # Save the latest candle data (you can modify this to your specific use case)
                    self.latest_candle_data = latest_candle_data

                else:
                    self.logger.warning("No data available for the next candle.")

        except Exception as e:
            self.logger.exception("Error fetching latest candle data: %s", str(e))
