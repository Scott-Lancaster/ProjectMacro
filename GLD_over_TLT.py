#!/usr/bin/env python3

##WIP

import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Configuration ---
start_date = datetime.now() - timedelta(days=30*365)  # ~30 years
end_date = datetime.now()

# --- Fetch GLD and TLT price data ---
print("Fetching GLD and TLT data from Yahoo Finance...")
tickers = ['GLD', 'TLT']
data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

# Drop rows where either is missing
data = data.dropna()

# Calculate GLD / TLT ratio
ratio = data['GLD'] / data['TLT']

# --- Fetch recession data from FRED ---
print("Fetching recession data from FRED...")
recession = web.DataReader('USREC', 'fred', start_date, end_date)

# --- Plotting ---
plt.figure(figsize=(14, 7))

# Plot the GLD/TLT ratio
plt.plot(ratio.index, ratio, label='GLD / TLT Ratio', color='gold', linewidth=2)

# Add recession shading
in_recession = False
recession_start = None

for date, row in recession.iterrows():
    date = date.to_pydatetime()  # Convert Timestamp to datetime
    if date not in ratio.index:
        continue  # Skip if no price data

    if row['USREC'] == 1 and not in_recession:
        in_recession = True
        recession_start = date
    elif row['USREC'] == 0 and in_recession:
        in_recession = False
        plt.axvspan(recession_start, date, color='gray', alpha=0.3, label='Recession' if 'Recession' not in plt.gca().get_legend_handles_labels()[1] else "")

# Shade final period if still in recession
if in_recession:
    plt.axvspan(recession_start, ratio.index[-1], color='gray', alpha=0.3)

# Styling
plt.axhline(y=1.0, color='black', linestyle='--', linewidth=1.0, alpha=0.7)
plt.title('GLD / TLT Ratio Over the Past 30 Years', fontsize=16, pad=15)
plt.xlabel('Year', fontsize=12)
plt.ylabel('GLD / TLT (Gold vs Long-Term Bonds)', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# Format x-axis
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(base=2))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()