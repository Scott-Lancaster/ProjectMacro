#!/usr/bin/env python3
import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'  # Suppress macOS warning

"""
===============================================================================
10Y - 2Y TREASURY YIELD SPREAD | Dark Mode
===============================================================================

WHAT IT SHOWS
  Daily spread = 10-Year Treasury Yield – 2-Year Treasury Yield (%)
  Shaded U.S. recessions (NBER)

WHY IT MATTERS
  Negative spread (inversion) → Strong recession signal (has predicted every U.S. recession since 1955)
  Positive → Normal yield curve (growth)
  → Key leading indicator for Fed policy and market risk

DATA SOURCES (FRED)
  T10Y2Y: https://fred.stlouisfed.org/series/T10Y2Y   (1980–)
  USREC:  https://fred.stlouisfed.org/series/USREC    (1854–)

DATA FREQUENCY: Daily (market close; T10Y2Y updated ~3:30 PM ET)

ZOOM: Set START_YEAR / END_YEAR
===============================================================================
"""

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# ———————————————— ZOOM SETTINGS ————————————————
START_YEAR = 1995
END_YEAR   = None  # None = today
# ———————————————————————————————————————————————

# Config
start = datetime(START_YEAR, 1, 1)
end   = datetime.now() if END_YEAR is None else datetime(END_YEAR, 12, 31)

# Fetch data
yield_curve = web.DataReader('T10Y2Y', 'fred', start, end)
recession = web.DataReader('USREC', 'fred', start, end)

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

# Yield spread — LIGHT GREY LINE
ax.plot(yield_curve.index, yield_curve['T10Y2Y'], color='#cccccc', linewidth=1.8, label='10Y - 2Y Spread')

# Recession shading
in_recession = False
recession_added = False

for date, row in recession.iterrows():
    if row['USREC'] == 1 and not in_recession:
        in_recession = True
        rec_start = date
    elif row['USREC'] == 0 and in_recession:
        in_recession = False
        label = 'Recession' if not recession_added else ""
        ax.axvspan(rec_start, date, color='#ff6b6b', alpha=0.15, label=label)
        recession_added = True

# Final recession
if in_recession:
    label = 'Recession' if not recession_added else ""
    ax.axvspan(rec_start, end, color='#ff6b6b', alpha=0.15, label=label)

# Zero line (inversion)
ax.axhline(0, color='#ff8c8c', linestyle='--', linewidth=1.5, alpha=0.8, label='Inversion (0%)')

# Title & labels
ax.set_title(f'10-Year minus 2-Year Treasury Yield Spread ({START_YEAR}–{END_YEAR or "Now"})\n'
             f'Last: {yield_curve["T10Y2Y"].iloc[-1]:.2f}%', 
             color='white', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('Year', color='white')
ax.set_ylabel('Spread (%)', color='white')

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
latest = yield_curve.iloc[-1]['T10Y2Y']
print(f"Latest: {latest:.2f}% | Data Frequency: Daily (updated ~3:30 PM ET)")