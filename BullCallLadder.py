import numpy as np
import matplotlib.pyplot as plt

def bull_call_ladder(stock_price, strike_price_long, strike_price_short, premium_long, premium_short, contracts):
    payoff = np.where(stock_price > strike_price_long, (stock_price - strike_price_long - premium_long) * contracts, 0)
    payoff += np.where(stock_price > strike_price_short, (strike_price_short - strike_price_long - premium_long + premium_short) * contracts, 0)
    payoff = np.where(stock_price > strike_price_short + premium_short, (stock_price - strike_price_short - premium_long + premium_short) * contracts, payoff)
    breakeven_upper = strike_price_long + premium_long + premium_short
    breakeven_lower = strike_price_short - premium_short
    
    return payoff, breakeven_upper, breakeven_lower

def plot_payoff(stock_price, payoff, breakeven_upper, breakeven_lower):
    plt.figure(figsize=(10, 6))
    plt.plot(stock_price, payoff, label='Bull Call Ladder Payoff')
    plt.axhline(0, color='black', lw=0.5)
    plt.axvline(breakeven_upper, color='r', linestyle='--', label='Upper Breakeven')
    plt.axvline(breakeven_lower, color='g', linestyle='--', label='Lower Breakeven')
    plt.xlabel('Stock Price')
    plt.ylabel('Profit/Loss')
    plt.title('Bull Call Ladder Payoff Diagram')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
stock_price = np.arange(0, 150, 1)
strike_price_long = 100
strike_price_short = 110
premium_long = 2.5
premium_short = 1.5
contracts = 1

payoff, breakeven_upper, breakeven_lower = bull_call_ladder(stock_price, strike_price_long, strike_price_short, premium_long, premium_short, contracts)
plot_payoff(stock_price, payoff, breakeven_upper, breakeven_lower)
