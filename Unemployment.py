#!/usr/bin/env python3
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# Function to print the rate of change with appropriate color
def print_colored_rate_of_change(rate, period):
    if rate > 0:
        # Red color for negative rate of change
        print(f"The {period} rate of change is: \033[91m{rate:.2f}%\033[0m")
    else:
        # Green color for positive rate of change
        print(f"The {period} rate of change is: \033[92m{rate:.2f}%\033[0m")

# Set the start and end dates
start_date = datetime.now() - pd.DateOffset(years=30)
end_date = datetime.now()

# Fetch the unemployment rate data from FRED
unemployment_rate = web.DataReader('UNRATE', 'fred', start_date, end_date)

# Calculate the 3 month rate of change
three_month_roc = ((unemployment_rate - unemployment_rate.shift(3)) / unemployment_rate.shift(3)) * 100
# Calculate the 6 month rate of change
six_month_roc = ((unemployment_rate - unemployment_rate.shift(6)) / unemployment_rate.shift(6)) * 100
# Calculate the 1 year rate of change
one_year_roc = ((unemployment_rate - unemployment_rate.shift(12)) / unemployment_rate.shift(12)) * 100

# Print the latest rates of change
print_colored_rate_of_change(three_month_roc.iloc[-1].values[0], '3 month')
print_colored_rate_of_change(six_month_roc.iloc[-1].values[0], '6 month')
print_colored_rate_of_change(one_year_roc.iloc[-1].values[0], '1 year')

# Fetch the recession data from FRED (US Recession Indicator)
recession_data = web.DataReader('USREC', 'fred', start_date, end_date)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(unemployment_rate.index, unemployment_rate['UNRATE'], label='US Unemployment Rate', color='blue')

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

plt.title('US Unemployment Rate Over the Last 30 Years')
plt.xlabel('Year')
plt.ylabel('Unemployment Rate (%)')
plt.legend()
plt.grid(True)
plt.show()
