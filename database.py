import logging
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from custom_logger import LoggerConfig
from configuration_default import DefaultConfig

class DatabaseManager:
    """
    Класс для управления базой данных.

    Attributes:
        connection (psycopg2.extensions.connection): Соединение с базой данных.
        cursor (psycopg2.extensions.cursor): Курсор для выполнения операций с базой данных.
    """

    def __init__(self):
        """
        Инициализация объекта DatabaseManager.

        Подключается к базе данных и инициализирует курсор.

        Raises:
            Exception: В случае ошибки подключения к базе данных.
        """
        load_dotenv(dotenv_path=r'C:\Users\wangr\PycharmProjects\pythonProject9\config\db_credintials.env')

        # Use the provided database_name or default from DefaultConfig
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_DATABASE")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_port = os.getenv("DB_PORT")

        # Конфигурация логгера
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

        try:
            # Установление соединения
            self.connection = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )

            self.cursor = self.connection.cursor()
            self.logger.debug('Успешно подключено к базе данных.')
        except Exception as e:
            self.logger.exception(f'Ошибка подключения к базе данных: {str(e)}')
            raise e

    def some_method(self):
        self.logger.debug('Debug message')
        self.logger.info('Informational message')
        self.logger.warning('Warning message')
        self.logger.error('Error message')
        self.logger.exception('Critical message')

    def insert_data(self, data):
        """
        Вставка данных в таблицу.

        Args:
            data (list): Данные для вставки в виде списка кортежей.

        Raises:
            Exception: В случае ошибки вставки данных.
        """
        cursor = None  # Инициализация курсора

        try:
            # Fetch the table name from default settings
            table_name = DefaultConfig().table_name

            cursor = self.connection.cursor()
            # Извлечение меток времени из новых данных
            new_timestamps = set([item[0] for item in data])

            # Получение меток времени существующих записей
            cursor.execute(f"SELECT timestamp FROM {table_name}")
            existing_timestamps = {str(row[0]) for row in cursor.fetchall()}

            # Фильтрация данных, которые уже присутствуют в базе данных
            new_data = [row for row in data if str(row[0]) not in existing_timestamps]

            # Вставка новых данных
            if new_data:
                cursor.executemany(
                    f"INSERT INTO {table_name} (timestamp, open_price, high_price, low_price, close_price, volume) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    new_data
                )
                self.connection.commit()
                self.logger.info("Успешная вставка данных.")
            else:
                self.logger.info("Нет новых данных для вставки.")

        except Exception as e:
            self.connection.rollback()
            self.logger.exception(f"Ошибка при вставке данных: {str(e)}")

        finally:
            if cursor:  # Проверка, что курсор не равен None
                cursor.close()

    def fetch_data_for_chart(self):
        """
        Извлекает данные из указанной таблицы для отображения на графике.

        Returns:
            pd.DataFrame: Фрейм данных с требуемыми данными.
        """
        try:
            table_name = DefaultConfig().table_name
            cursor = self.connection.cursor()
            cursor.execute(
                f"SELECT timestamp, open_price, high_price, low_price, close_price, volume FROM {table_name}")
            data = cursor.fetchall()
            cursor.close()
            columns = ['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            self.logger.error(f"Failed to fetch data for chart: {str(e)}")
            return pd.DataFrame()



    def close_connection(self):
        self.cursor.close()
        self.connection.close()