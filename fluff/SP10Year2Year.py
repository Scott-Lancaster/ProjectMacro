import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# Set the start and end dates
start_date = datetime.now() - pd.DateOffset(years=30)
end_date = datetime.now()

# Fetch the yield curve data from FRED
yield_curve = web.DataReader('T10Y2Y', 'fred', start_date, end_date)

# Fetch the recession data from FRED (US Recession Indicator)
recession_data = web.DataReader('USREC', 'fred', start_date, end_date)

# Fetch the S&P 500 index data from Yahoo Finance using yfinance
sp500 = yf.download('^GSPC', start=start_date, end=end_date)['Adj Close']

# Plotting
fig, ax1 = plt.subplots(figsize=(12, 8))

ax1.plot(yield_curve, label='10-Year minus 2-Year Treasury Yield', color='blue')
ax1.set_xlabel('Year')
ax1.set_ylabel('Yield Difference (%)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Add shading for recessions
in_recession = False
for date, value in recession_data.iterrows():
    if value.USREC == 1 and not in_recession:
        in_recession = True
        recession_start = date
    elif value.USREC == 0 and in_recession:
        in_recession = False
        ax1.axvspan(recession_start, date, color='grey', alpha=0.3)

# Check if still in recession at end of data and shade if necessary
if in_recession:
    ax1.axvspan(recession_start, end_date, color='grey', alpha=0.3)

# Making the x-axis line bolder
ax1.axhline(y=0, color='black', linewidth=2.0)

# Create a secondary y-axis for the S&P 500
ax2 = ax1.twinx()
ax2.plot(sp500, label='S&P 500 Index', color='lightgray')
ax2.set_ylabel('S&P 500 Index', color='gray')
ax2.tick_params(axis='y', labelcolor='gray')

# Add legends
fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))

plt.title('10-Year minus 2-Year Treasury Yield and S&P 500 Over the Last 30 Years')
plt.grid(True)
plt.show()
