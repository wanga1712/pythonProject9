import pandas as pd
import numpy as np
import plotly.graph_objects as go
from database import DatabaseManager  # Import your DatabaseManager class

# Set the display options for Pandas
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.expand_frame_repr', False)  # Don't wrap lines

# Create an instance of DatabaseManager
db_manager = DatabaseManager()

# Fetch data for chart
data = db_manager.fetch_data_for_chart()

# Assuming the DataFrame contains the required columns like 'timestamp' and 'close_price'
# Replace with the actual column names from your DataFrame

# Convert 'timestamp' to datetime and set it as the index
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.set_index('timestamp', inplace=True)


def calculate_moving_averages(data):
    data['3_day_ma_shifted'] = data['close_price'].rolling(window=3).mean().shift(3)
    data['5_day_ma_shifted'] = data['close_price'].rolling(window=5).mean().shift(5)
    data['25_day_ma_shifted'] = data['close_price'].rolling(window=25).mean().shift(25)
    return data


# Calculate moving averages
data_with_ma = calculate_moving_averages(data)
# Convert DataFrame to string and print
data_str = data.to_string()

# Print the DataFrame with moving averages
print(data_with_ma)


def calculate_beer_points(price_data, length=10):
    n = len(price_data)
    pivot_points = []

    for i in range(1, n - 1):  # Adjusted the range to check the next candle only
        high = price_data['high_price'].iloc[i]
        low = price_data['low_price'].iloc[i]

        # Check for potential pivot points
        if high > price_data['high_price'].iloc[i - 1] and high > price_data['high_price'].iloc[i + 1]:
            potential_pivot = {'Pivot Type': 'Potential High', 'Pivot Value': high, 'Date': price_data.index[i]}
        elif low < price_data['low_price'].iloc[i - 1] and low < price_data['low_price'].iloc[i + 1]:
            potential_pivot = {'Pivot Type': 'Potential Low', 'Pivot Value': low, 'Date': price_data.index[i]}
        else:
            potential_pivot = None

        # Append confirmed pivot points
        if potential_pivot:
            pivot_points.append(potential_pivot)

    df_pivots = pd.DataFrame(pivot_points)
    return df_pivots



# ------------------------------------------------
def display_chart(data_with_ma, beer_points_df):
    # Create a candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=data_with_ma.index,
                                         open=data_with_ma['open_price'],
                                         high=data_with_ma['high_price'],
                                         low=data_with_ma['low_price'],
                                         close=data_with_ma['close_price'])])

    # Add the moving averages with specified colors
    fig.add_trace(go.Scatter(x=data_with_ma.index, y=data_with_ma['3_day_ma_shifted'], mode='lines', name='3-day MA',
                             line=dict(color='green')))  # Set color to green

    fig.add_trace(go.Scatter(x=data_with_ma.index, y=data_with_ma['5_day_ma_shifted'], mode='lines', name='5-day MA',
                             line=dict(color='blue')))  # Set color to blue

    fig.add_trace(go.Scatter(x=data_with_ma.index, y=data_with_ma['25_day_ma_shifted'], mode='lines', name='25-day MA',
                             line=dict(color='red')))  # Set color to red

    # Add Beer points and connect them
    for i, row in beer_points_df.iterrows():
        marker_color = 'red' if 'High' in row['Pivot Type'] else 'green'
        marker_symbol = 'triangle-down' if 'High' in row['Pivot Type'] else 'triangle-up'
        pivot_value = row['Pivot Value']

        # Assuming 'Date' and 'Pivot Type' are the relevant columns
        fig.add_trace(go.Scatter(x=[row['Date']], y=[pivot_value],
                                 mode='markers',
                                 name=row['Pivot Type'],
                                 marker=dict(color=marker_color, size=10, symbol=marker_symbol)))

        # Connect points a, b, c
        if i > 0:
            prev_row = beer_points_df.iloc[i - 1]
            prev_pivot_value = prev_row['Pivot Value']
            fig.add_trace(go.Scatter(x=[prev_row['Date'], row['Date']], y=[prev_pivot_value, pivot_value],
                                     mode='lines',
                                     line=dict(color=marker_color, width=2)))

    # Customize the layout
    fig.update_layout(
        title='Candlestick Chart with Moving Averages and Beer Points',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    # Show the figure
    print("\nBeer Points Data:")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(beer_points_df.tail(100))

    fig.show()


# Usage
# Assuming you have a DataFrame called 'data' containing the required columns
# Replace with the actual column names from your DataFrame

# Calculate moving averages
data_with_ma = calculate_moving_averages(data)

# Calculate beer points
beer_points_df = calculate_beer_points(data)

# Assuming beer_points_df contains the pivot points data
# Call the function to plot the pivot points
# plot_pivot_points(beer_points_df)

# # Display the chart
display_chart(data_with_ma, beer_points_df)
