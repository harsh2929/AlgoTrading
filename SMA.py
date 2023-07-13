import pandas as pd
import numpy as np

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def generate_signals(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    signals['short_sma'] = calculate_sma(data, short_window)
    signals['long_sma'] = calculate_sma(data, long_window)

    signals['signal'] = np.where(signals['short_sma'] > signals['long_sma'], 1, -1)

    signals['positions'] = signals['signal'].diff()

    return signals

def backtest_strategy(data, signals, initial_capital, risk_percentage):
    combined = pd.concat([data, signals], axis=1).dropna()

    portfolio = pd.DataFrame(index=combined.index)
    portfolio['positions'] = signals['positions']
    portfolio['price'] = combined['Close']

    portfolio['holdings'] = (portfolio['positions'].cumsum() * portfolio['price']) * (1 - risk_percentage)
    portfolio['cash'] = initial_capital - (portfolio['positions'].cumsum() * portfolio['price']).cumsum()

    portfolio['total'] = portfolio['cash'] + portfolio['holdings']

    portfolio['returns'] = portfolio['total'].pct_change()

    return portfolio

# Example usage
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

short_window = 50
long_window = 200

signals = generate_signals(data['Close'], short_window, long_window)

initial_capital = 100000
risk_percentage = 0.02

portfolio = backtest_strategy(data, signals, initial_capital, risk_percentage)

print(portfolio)
