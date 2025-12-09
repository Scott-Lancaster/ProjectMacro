#!/usr/bin/env python3
import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'  # Suppress macOS warning

"""
===============================================================================
US UNEMPLOYMENT RATE | Dark Mode
===============================================================================

WHAT IT SHOWS
  Monthly US unemployment rate (%)
  Shaded U.S. recessions (NBER)

WHY IT MATTERS
  Unemployment rises when companies cut jobs amid slowing growth — a lagging but confirming recession signal.
  The Fed watches it closely (dual mandate: full employment + stable prices); high levels prompt rate cuts.
  3-month rises above 0.5% (Sahm Rule) have signaled every recession since 1950.

DATA SOURCES (FRED)
  UNRATE: https://fred.stlouisfed.org/series/UNRATE   (1948–)
  USREC:  https://fred.stlouisfed.org/series/USREC    (1854–)

DATA FREQUENCY: Monthly (released first Friday ~8:30 AM ET)

ZOOM: Set START_YEAR
===============================================================================
"""

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# Function to print the rate of change with appropriate color
def print_colored_rate_of_change(rate, period):
    color = '\033[91m' if rate > 0 else '\033[92m'  # Red for positive, green for negative
    print(f"The {period} rate of change is: {color}{rate:.2f}%\033[0m")

# ———————————————— ZOOM SETTINGS ————————————————
START_YEAR = 1950  # Set your desired start year here
# ———————————————————————————————————————————————

# Config
start = datetime(START_YEAR, 1, 1)
end   = datetime.now()

# Fetch data
unemployment_rate = web.DataReader('UNRATE', 'fred', start, end)
recession         = web.DataReader('USREC',  'fred', start, end)

# Calculate rates of change
three_month_roc = ((unemployment_rate - unemployment_rate.shift(3)) / unemployment_rate.shift(3)) * 100
six_month_roc   = ((unemployment_rate - unemployment_rate.shift(6)) / unemployment_rate.shift(6)) * 100
one_year_roc    = ((unemployment_rate - unemployment_rate.shift(12)) / unemployment_rate.shift(12)) * 100

# Print latest rates
print_colored_rate_of_change(three_month_roc.iloc[-1].values[0], '3 month')
print_colored_rate_of_change(six_month_roc.iloc[-1].values[0], '6 month')
print_colored_rate_of_change(one_year_roc.iloc[-1].values[0], '1 year')

# ———————————————— DARK MODE STYLE ————————————————
plt.style.use('dark_background')
plt.rcParams.update({
    'figure.facecolor': '#0a0a0a',
    'axes.facecolor':   '#0a0a0a',
    'axes.edgecolor':   '#333333',
    'axes.labelcolor':  'white',
    'text.color':       'white',
    'xtick.color':      'white',
    'ytick.color':      'white',
    'grid.color':       '#2a2a2a',
    'grid.alpha':       0.3,
    'font.size':        11,
    'legend.facecolor': '#1a1a1a',
    'legend.edgecolor': '#333333',
    'legend.fontsize':  10,
})

# Plot
fig, ax = plt.subplots(figsize=(14, 7))

# Unemployment line — thinner, blue
ax.plot(unemployment_rate.index, unemployment_rate['UNRATE'],
        color='#4da6ff', linewidth=1.4, label='US Unemployment Rate')

# Recession shading — darker red
in_recession = False
recession_added = False

for date, row in recession.iterrows():
    if row['USREC'] == 1 and not in_recession:
        in_recession = True
        rec_start = date
    elif row['USREC'] == 0 and in_recession:
        in_recession = False
        label = 'Recession' if not recession_added else ""
        ax.axvspan(rec_start, date, color='#cc4444', alpha=0.25, label=label)
        recession_added = True

if in_recession:
    label = 'Recession' if not recession_added else ""
    ax.axvspan(rec_start, end, color='#cc4444', alpha=0.25, label=label)

# Title & labels
ax.set_title(f'US Unemployment Rate ({START_YEAR}–Now)\n'
             f'Last: {unemployment_rate["UNRATE"].iloc[-1]:.2f}%',
             color='white', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('Year', color='white')
ax.set_ylabel('Unemployment Rate (%)', color='white')

# Legend
ax.legend(loc='upper left', framealpha=0.95)

# Grid & formatting
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# ———————————————— FINAL SUMMARY ————————————————
latest = unemployment_rate.iloc[-1]['UNRATE']
print(f"Latest: {latest:.2f}% | Data Frequency: Monthly (updated first Friday ~8:30 AM ET)")