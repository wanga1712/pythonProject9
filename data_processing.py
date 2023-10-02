class DataProcessor:
    def __init__(self, df):
        self.df = df

    def calculate_moving_average(self, window, offset):
        ma = self.df['Close Pricнапиши функцию, которая будет извеe'].rolling(window=window).mean()
        ma_shifted = ma.shift(offset)
        return ma_shifted

    def process_data(self, window=3, offset=3):
        # Calculate moving average
        ma_data = self.calculate_moving_average(window, offset)
        return ma_data