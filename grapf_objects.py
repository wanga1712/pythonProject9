import logging
import plotly.graph_objects as go
from database import DatabaseManager
import warnings
from custom_logger import LoggerConfig


class CandlestickChart:
    def __init__(self):

        # Конфигурация логгера
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

    def plot_chart(self):
        self.logger.info('Plotting candlestick chart...')

        try:
            db_manager = DatabaseManager()
            data = db_manager.fetch_data_for_chart()

            with warnings.catch_warnings():
                # Suppress the specific FutureWarning
                warnings.simplefilter(action='ignore', category=FutureWarning)

                fig = go.Figure(data=[go.Candlestick(x=data['timestamp'],
                                                     open=data['open_price'],
                                                     high=data['high_price'],
                                                     low=data['low_price'],
                                                     close=data['close_price'])])

                fig.update_layout(
                    title='Candlestick Chart',
                    yaxis_title='Price',
                    xaxis_title='Timestamp'
                )
                fig.show()

            self.logger.info('Candlestick chart plot completed.')
        except Exception as e:
            self.logger.exception(f'Error occurred while plotting candlestick chart: {str(e)}')