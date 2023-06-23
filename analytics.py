import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

ticker = "AAPL"
start_date = "2010-01-01"
end_date = "2022-12-31"

data = yf.download(ticker, start=start_date, end=end_date)

data['SMA50'] = data['Close'].rolling(window=50).mean()
data['SMA200'] = data['Close'].rolling(window=200).mean()

data['Signal'] = np.where(data['SMA50'] > data['SMA200'], 1, -1)

data['Return'] = data['Close'].pct_change()

data['StrategyReturn'] = data['Signal'].shift(1) * data['Return']

data['CumulativeReturn'] = (1 + data['StrategyReturn']).cumprod()

plt.figure(figsize=(10, 6))
plt.plot(data['CumulativeReturn'])
plt.title('Moving Average Crossover Strategy')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.grid(True)
plt.show()

total_return = data['CumulativeReturn'][-1] - 1
annualized_return = (1 + total_return) ** (252 / len(data)) - 1
annualized_volatility = data['StrategyReturn'].std() * np.sqrt(252)
sharpe_ratio = annualized_return / annualized_volatility

print(f"Total Return: {total_return:.2%}")
print(f"Annualized Return: {annualized_return:.2%}")
print(f"Annualized Volatility: {annualized_volatility:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
