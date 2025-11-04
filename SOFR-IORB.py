#!/usr/bin/env python3
"""
===============================================================================
REPO SPREAD MONITOR: SOFR-IORB → OBFR-IOER | Dark Mode
===============================================================================

WHAT IT SHOWS
  Daily spread = Repo Rate – Fed Floor Rate (in basis points)
  30-day moving average

WHY IT MATTERS
  Positive > 30 bp → Repo market stress
  Negative → Ample reserves
  → Early warning for rate cuts, QT risks, or banking strain

DATA SOURCES (FRED)
  OBFR: https://fred.stlouisfed.org/series/OBFR   (2016–)
  SOFR: https://fred.stlouisfed.org/series/SOFR   (2018–)
  IOER: https://fred.stlouisfed.org/series/IOER   (2008–2021)
  IORB: https://fred.stlouisfed.org/series/IORB   (2021–)

DATA FREQUENCY: Daily (published each business day ~8-9 AM ET for repo rates, ~4:30 PM ET for floor rates)

ZOOM: Set START_YEAR / END_YEAR
===============================================================================
"""

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# ———————————————— ZOOM SETTINGS ————————————————
START_YEAR = 2019
END_YEAR   = None  # None = today
# ———————————————————————————————————————————————

# Config
start = datetime(START_YEAR, 1, 1)
end   = datetime.now() if END_YEAR is None else datetime(END_YEAR, 12, 31)
sofr_start = datetime(2018, 4, 3)
iorb_start = datetime(2021, 7, 29)

# Fetch data
obfr = web.DataReader('OBFR', 'fred', start, end)
sofr = web.DataReader('SOFR', 'fred', start, end)
ioer = web.DataReader('IOER', 'fred', start, end)
iorb = web.DataReader('IORB', 'fred', start, end)

# Build repo & floor
repo  = pd.concat([obfr, sofr], axis=1).max(axis=1).to_frame('Repo')
floor = pd.concat([ioer, iorb], axis=1).max(axis=1).to_frame('Floor')

# Merge & compute
data = pd.concat([repo, floor], axis=1).dropna()
data['Spread_bp'] = (data['Repo'] - data['Floor']) * 100
data['MA_30d']    = data['Spread_bp'].rolling(30, min_periods=1).mean()

# Label metric
data['Metric'] = 'OBFR – IOER'
data.loc[data.index >= sofr_start, 'Metric'] = 'SOFR – IOER'
data.loc[data.index >= iorb_start, 'Metric'] = 'SOFR – IORB'

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

# Lines
ax.plot(data.index, data['Spread_bp'], color='#4da6ff', linewidth=1.2, label='Daily Spread')
ax.plot(data.index, data['MA_30d'],    color='#cc5555', linewidth=2.5, label='30-Day MA')  # Muted red

# Transitions
for d, txt, col in [(sofr_start, 'SOFR', '#4da6ff'), (iorb_start, 'IORB', '#ff8c8c')]:
    if start <= d <= end:
        ax.axvline(d, color=col, linestyle=':', linewidth=1.8, alpha=0.8)
        ax.text(d, data['Spread_bp'].max() * 0.94, f' {txt}', color=col, fontsize=9, ha='left')

# Stress zone
ax.fill_between(data.index, 30, data['Spread_bp'].max(), color='#ff6b6b', alpha=0.12, label='Stress (>30 bp)')

# Zero line
ax.axhline(0, color='#888888', linestyle='--', linewidth=1.2, alpha=0.6)

# Title & labels
ax.set_title(f'Repo Spread vs. Fed Floor Rate ({START_YEAR}–{END_YEAR or "Now"})\n'
             f'Current: {data["Metric"].iloc[-1]}', 
             color='white', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('Date', color='white')
ax.set_ylabel('Spread (basis points)', color='white')

# Legend
ax.legend(loc='upper left', framealpha=0.95)

# Grid
ax.grid(True, alpha=0.3)

# X-axis
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2))
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# ———————————————— FINAL SUMMARY ————————————————
latest = data.iloc[-1]
print(f"Latest: {latest['Spread_bp']:.1f} bp | 30d MA: {latest['MA_30d']:.1f} bp | {latest['Metric']}")