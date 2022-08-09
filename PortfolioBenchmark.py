import yfinance as yf
import pandas as pd
import numpy as np
from configparser import ConfigParser
from matplotlib import pyplot as plt

# Read in benchmark ticker, initial investment and risk-free return (in percentages) here
config = ConfigParser()
config.read("config.ini")
benchmark_ticker = config["configuration"]["benchmark_ticker"]
initial_investment = float(config["configuration"]["initial_investment"])
rfr = float(config["configuration"]["risk_free_return"])

# Read in csv file as DataFrame, find initial investment date and find tickers traded
df = pd.read_csv("Portfolio.csv", index_col=0, skipinitialspace=True)
start_date = min(df.index)
tickers = set(df["Ticker"])

# Get benchmark prices and calculate differences to price on start_date
benchmark_prices = yf.Ticker(benchmark_ticker).history(start=start_date)["Close"][start_date:]
benchmark_differences = 100 * (benchmark_prices / benchmark_prices[start_date] - 1)

# Create portfolio columns
portfolio_columns = dict()
for ticker in tickers:
    portfolio_columns[ticker + " Amount"] = [0]
    portfolio_columns[ticker + " Price"] = [0]

portfolio_columns["Invested"] = [0]
portfolio_columns["Realized"] = [0]

# Create portfolio and portfolio_differences DataFrames with same indices as benchmark
portfolio = pd.DataFrame(index=benchmark_prices.index, data=portfolio_columns, dtype=float)
portfolio_differences = pd.DataFrame(index=benchmark_prices.index, data={"Close": [0]}, dtype=float)

# Create dictionary with historical prices for tickers
prices = {ticker: pd.DataFrame(yf.Ticker(ticker).history(start=start_date)["Close"][start_date:]) for ticker in tickers}

# Populate portfolio columns using historical prices and read in DataFrame
for i in range(len(df)):
    ticker = df["Ticker"][i]
    amount = df["Amount"][i]
    price = df["Price"][i]

    # Check if ticker is being bought or sold
    if amount > 0:
        portfolio.loc[df.index[i]:, ticker + " Price"] += amount * price
        portfolio.loc[df.index[i]:, "Invested"] += amount * price
    elif amount < 0:
        average_price = portfolio.loc[df.index[i], ticker + " Price"] / portfolio.loc[df.index[i], ticker + " Amount"]
        portfolio.loc[df.index[i]:, ticker + " Price"] += amount * average_price
        portfolio.loc[df.index[i]:, "Invested"] += amount * average_price
        portfolio.loc[df.index[i]:, "Realized"] += amount * (average_price - price) / initial_investment * 100
    else:
        continue
    portfolio.loc[df.index[i]:, ticker + " Amount"] += amount

# Populate portfolio_differences
for ticker in tickers:
    portfolio_differences += pd.DataFrame(prices[ticker]).multiply(portfolio[ticker + " Amount"], axis=0).sub(
        portfolio[ticker + " Price"], axis=0) / initial_investment * 100

portfolio_total = portfolio_differences.add(portfolio["Realized"], axis=0)

# Calculate key stats
correlation = float(np.corrcoef(portfolio_total, benchmark_differences, rowvar=False)[0, 1])
portfolio_std = float(np.std(portfolio_total, axis=0))
benchmark_std = float(np.std(benchmark_differences, axis=0))
beta = correlation * portfolio_std / benchmark_std
bus_days = float(np.busday_count(start_date, np.datetime64("today")))
rfr_adjusted = 100 * ((1 + rfr / 100) ** (bus_days / 252) - 1)
alpha = (float(portfolio_total.iloc[-1]) - rfr_adjusted - beta * (float(benchmark_differences.iloc[-1]) - rfr_adjusted))

portfolio_low = float(portfolio_total.min())
portfolio_high = float(portfolio_total.max())
benchmark_low = float(benchmark_differences.min())
benchmark_high = float(benchmark_differences.max())

key_stats = f"$\\alpha = {alpha:.3f}\\%$\n" \
            f"$\\beta = {beta:.3f}$\n" \
            f"correlation $= {correlation:.3f}$\n" \
            f"portfolio range $= ({portfolio_low:.2f}\\%, {portfolio_high:.2f}\\%)$\n" \
            f"benchmark range $= ({benchmark_low:.2f}\\%, {benchmark_high:.2f}\\%)$"

# Plot results
figure = plt.figure(figsize=(11, 7))
grid_size = (3, 5)
axes = [[None for j in range(2)] for i in range(3)]

axes[0][0] = plt.subplot2grid(grid_size, (0, 0), colspan=grid_size[1] - 1)
axes[1][0] = plt.subplot2grid(grid_size, (1, 0), colspan=grid_size[1] - 1)
axes[2][0] = plt.subplot2grid(grid_size, (2, 0), colspan=grid_size[1] - 1)
axes[0][1] = plt.subplot2grid(grid_size, (0, grid_size[1] - 1))
axes[1][1] = plt.subplot2grid(grid_size, (1, grid_size[1] - 1))
axes[2][1] = plt.subplot2grid(grid_size, (2, grid_size[1] - 1))

axes[0][0].plot(portfolio_differences, label="Portfolio")
axes[0][0].set_title("Unrealized P&L")
axes[0][0].set_xlabel("Date")
axes[0][0].set_ylabel("% Change")
axes[0][0].legend()
axes[0][0].grid(axis="y")

axes[1][0].plot(portfolio["Realized"], label="Portfolio")
axes[1][0].set_title("Realized P&L")
axes[1][0].set_xlabel("Date")
axes[1][0].set_ylabel("% Change")
axes[1][0].legend()
axes[1][0].grid(axis="y")

axes[2][0].plot(portfolio_total, label="Portfolio")
axes[2][0].plot(benchmark_differences, label=f"Benchmark ({benchmark_ticker})")
axes[2][0].set_title("Total P&L")
axes[2][0].set_xlabel("Date")
axes[2][0].set_ylabel("% Change")
axes[2][0].legend()
axes[2][0].grid(axis="y")

axes[0][1].axis("off")
axes[0][1].set_title("Key Stats")

axes[1][1].axis("off")

axes[2][1].axis("off")
axes[2][1].text(0, 1, key_stats, horizontalalignment="left", verticalalignment="top")

plt.tight_layout()
plt.show()
