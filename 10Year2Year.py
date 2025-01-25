import pandas as pd
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

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(yield_curve, label='10-Year minus 2-Year Treasury Yield')

# Add shading for recessions
in_recession = False
for date, value in recession_data.iterrows():
    if value.USREC == 1 and not in_recession:
        in_recession = True
        recession_start = date
    elif value.USREC == 0 and in_recession:
        in_recession = False
        plt.axvspan(recession_start, date, color='grey', alpha=0.3)

# Check if still in recession at end of data and shade if necessary
if in_recession:
    plt.axvspan(recession_start, end_date, color='grey', alpha=0.3)

# Making the x-axis line bolder
plt.axhline(y=0, color='black', linewidth=2.0)

plt.title('10-Year minus 2-Year Treasury Yield Over the Last 30 Years')
plt.xlabel('Year')
plt.ylabel('Yield Difference (%)')
plt.legend()
plt.grid(True)
plt.show()
