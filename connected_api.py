from binance_f import RequestClient
from io import StringIO
import sys
import logging
from custom_logger import LoggerConfig


class ConnectedAPI:
    """
    Класс ConnectedAPI представляет подключение к API.

    Parameters:
        api_key (str): Ключ API для аутентификации.
        secret_key (str): Секретный ключ для дополнительной аутентификации.

    Attributes:
        api_key (str): Ключ API для аутентификации.
        secret_key (str): Секретный ключ для дополнительной аутентификации.
        logger (logging.Logger): Объект логгера для записи сообщений.

    Methods:
        __init__: Инициализация объекта ConnectedAPI с указанием ключей API и настройки логгера.
    """

    def __init__(self, api_key, secret_key):
        """
        Инициализация объекта ConnectedAPI.

        Parameters:
            api_key (str): Ключ API для аутентификации.
            secret_key (str): Секретный ключ для дополнительной аутентификации.
        """
        self.api_key = api_key
        self.secret_key = secret_key

        # Конфигурация логгера
        self.logger = logging.getLogger(__name__)
        LoggerConfig.configure_logger(self.logger)

        if self.secret_key:
            self.logger.debug("Успешно получены секретные ключи")
        else:
            self.logger.error("Секретный ключ не найден")

    def some_method(self):
        self.logger.debug('Debug message')
        self.logger.info('Informational message')
        self.logger.warning('Warning message')
        self.logger.error('Error message')
        self.logger.exception('Critical message')

    def get_account_balance(self):
        """
        Получает баланс аккаунта.

        Метод подавляет вывод, используя StringIO, и восстанавливает стандартный вывод после завершения запроса к API.
        Баланс аккаунта извлекается с использованием соответствующего эндпоинта.

        Возвращает:
            tuple: Кортеж, содержащий балансы аккаунта и захваченный вывод.

            Структура возвращаемого кортежа:
                - balances (list): Список кортежей вида (asset, balance), представляющих валюту и соответствующий баланс.
                - output_data (str): Захваченный вывод.
        """
        try:
            # Подавление вывода с использованием StringIO
            output = StringIO()
            sys.stdout = output

            client = RequestClient(api_key=self.api_key, secret_key=self.secret_key, testnet=True)
            account_balance = client.get_balance_v2()  # Используется правильный эндпоинт

            # Восстановление стандартного вывода
            sys.stdout = sys.__stdout__

            # Получение захваченного вывода
            output_data = output.getvalue().strip()  # Удаление завершающего перевода строки

            # Обработка данных о балансе аккаунта
            if account_balance is not None:
                balances = []
                for balance in account_balance:
                    if float(balance.balance) != 0:
                        balances.append((balance.asset, balance.balance))
                # Log successful balance retrieval
                self.logger.debug("Баланс успешно получен.")
            else:
                balances = []
                # Log that no balance was received
                self.logger.error("Не удалось получить баланс.")
        except Exception as e:
            # Log any exceptions that occur during balance retrieval
            self.logger.exception("Ошибка при получении баланса: %s", str(e))
            balances = []  # Return empty balances if an error occurs

        # Возврат балансов и захваченного вывода
        return balances, output_data

    def get_open_positions(self):
        """
        Получает открытые позиции.

        Метод подавляет вывод, используя StringIO, и восстанавливает стандартный вывод после запроса к API.
        Извлекает данные об открытых позициях с использованием соответствующего эндпоинта.

        Returns:
            tuple: Кортеж, содержащий открытые позиции и захваченный вывод.

        Структура возвращаемого кортежа:
            - positions (list): Список кортежей вида (symbol, positionSide, positionAmt),
              представляющих символ, направление позиции и соответствующий объем позиции.
            - output_data (str): Захваченный вывод.
        """
        # Подавление вывода с использованием StringIO
        output = StringIO()
        sys.stdout = output

        client = RequestClient(api_key=self.api_key, secret_key=self.secret_key, testnet=True)
        open_positions = client.get_position_v2()  # Используется правильный эндпоинт

        # Восстановление стандартного вывода
        sys.stdout = sys.__stdout__

        # Получение захваченного вывода
        output_data = output.getvalue().strip()  # Удаление завершающего перевода строки

        if open_positions is not None:
            # Обработка данных об открытых позициях
            positions = [(position.symbol, position.positionSide, position.positionAmt) for position in open_positions
                         if float(position.positionAmt) != 0]

            # Log success message
            self.logger.debug("Успешно получены данные по открытым позициям.")
        else:
            positions = []

            # Log error message
            self.logger.error("Не удалось получить данные по открытым позициям.")

        # Возврат позиций и захваченного вывода
        return positions, output_data
