# -*- coding: utf-8 -*-
"""
Created on Tue Sep 2 7:20:20 2025

@author: thoma
"""





#---------------------------------------------------------------


import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



sns.set(style="darkgrid")



assets=['TSM','7203.T','GC=F','ZW=F','NG=F','URA','KC=F']
#commodities and Stocks
start_date = '2020-03-01'
#Y-M-D
end_date = '2023-03-01'
lookback = 20  # SMA,20 days 

#-----------------------------------------

raw = yf.download(assets, start=start_date, end=end_date)
if 'Adj Close' in raw.columns:
    data = raw['Adj Close'].dropna()
else:
    data = raw['Close'].dropna()



sma = data.rolling(window=lookback).mean()
signal = (data > sma).astype(int)  # 1 = long and  0 = cash


returns = data.pct_change().dropna()

equal_weights = np.repeat(1/len(assets), len(assets))

inv_vol = 1 / returns.std()

risk_parity_weights = inv_vol / inv_vol.sum()


#-----------------------------------------------------










# Backtest portfolio


def backtest(weights, name="Portfolio"):

    strat_returns = (returns * signal.shift(1)).dot(weights)

    equity_curve = (1 + strat_returns).cumprod()



    # Metrics

    cagr = (equity_curve.iloc[-1] ** (252/len(equity_curve)) - 1)

    vol = strat_returns.std() * np.sqrt(252)

    sharpe = strat_returns.mean()/strat_returns.std() * np.sqrt(252)



    downside = strat_returns[strat_returns < 0]

    sortino = strat_returns.mean()/downside.std() * np.sqrt(252) if len(downside) > 0 else np.nan



    cummax = equity_curve.cummax()

    drawdown = (equity_curve - cummax) / cummax

    max_dd = drawdown.min()



    return {

        "name": name,

        "curve": equity_curve,

        "cagr": cagr,

        "vol": vol,

        "sharpe": sharpe,

        "sortino": sortino,

        "max_dd": max_dd

    }



equal_portfolio = backtest(equal_weights, "Equal Weight")
rp_portfolio = backtest(risk_parity_weights, "Risk-Parity")





benchmark_returns = returns.dot(equal_weights)

benchmark_curve = (1 + benchmark_returns).cumprod()





#----------------------------------------------------------



def print_summary(name, port):

    print(f"--- {name} ---")

    print(f"CAGR: {port['cagr']:.2%}")

    print(f"Volatility: {port['vol']:.2%}")

    print(f"Max Drawdown: {port['max_dd']:.2%}")

    print(f"Sharpe Ratio: {port['sharpe']:.2f}")

    print(f"Sortino Ratio: {port['sortino']:.2f}")

    print("-"*40)



print_summary("Equal Weight", equal_portfolio)
print_summary("Risk Parity", rp_portfolio)





# single chart -----------------


plt.figure(figsize=(12,6))

plt.plot(equal_portfolio["curve"], label="Equal Weight")

plt.plot(rp_portfolio["curve"], label="Risk Parity")

plt.plot(benchmark_curve, label="Benchmark", linestyle="-.")

plt.title("Portfolio Strategies Backtest")

plt.xlabel("date")

plt.legend()

plt.ylabel("cumulative Return")


plt.show()



# ----------------------------------------------------------





plt.figure(figsize=(12,5))

drawdown = (equal_portfolio["curve"]/equal_portfolio["curve"].cummax()-1)
plt.plot(drawdown, color="purple")
plt.xlabel("date")
plt.ylabel("drawdown")
plt.title("Drawdown (Equal Weight Strategy)")


plt.show()



# -----------------------------

# Heatmap correlation between assets



plt.figure(figsize=(8,6))

sns.heatmap(returns.corr(), annot=True, cmap="coolwarm", center=0)

plt.title("Correlation Matrix of Assets")

plt.show()






# -----------------------------

summary = pd.DataFrame([

    {

        "Strategy": "Equal Weight",

        "CAGR": equal_portfolio['cagr'],

        "Sharpe Ratio": equal_portfolio['sharpe'],

        "Volatility": equal_portfolio['vol'],

        "Max Drawdown": equal_portfolio['max_dd']

    },

    {

        "Strategy": "Risk Parity",

        "CAGR": rp_portfolio['cagr'],

        "Sharpe Ratio": rp_portfolio['sharpe'],

        "Volatility": rp_portfolio['vol'],

        "Max Drawdown": rp_portfolio['max_dd']

    }

])

#-------------------------------------------

summary.to_csv("portfolio_summary.csv", index=False)

print("\nRésumé exporté dans 'portfolio_summary.csv'")








#_________________________________________________________________________













