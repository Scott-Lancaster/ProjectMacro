#!/usr/bin/env python3
import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'

"""
===============================================================================
US CREDIT CARD / REVOLVING DEBT | Dark Mode
===============================================================================

WHAT IT SHOWS
  Monthly total revolving consumer credit (primarily credit cards)
  Nominal (blue) and optional inflation-adjusted real (green) in trillions $
  Shaded U.S. recessions (NBER)

WHY IT MATTERS
  Rapid debt growth often signals consumer stress (borrowing to maintain spending)
  Peaks frequently precede recessions; sharp drops occur during downturns
  Real debt (inflation-adjusted) reveals true burden vs. nominal illusion

DATA SOURCES (FRED)
  REVOLSL: Revolving Consumer Credit (millions $) – https://fred.stlouisfed.org/series/REVOLSL
  CPIAUCSL: CPI for inflation adjustment – https://fred.stlouisfed.org/series/CPIAUCSL
  USREC: Recession indicator – https://fred.stlouisfed.org/series/USREC

DATA FREQUENCY: Monthly

ZOOM: Set START_YEAR | Toggle INFLATION_ADJUSTED
===============================================================================
"""

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# ———————————————— OPTIONS ————————————————
START_YEAR = 2000
INFLATION_ADJUSTED = True   # False = nominal only | True = real (chained to latest $)
# ———————————————————————————————————————————————

start = datetime(START_YEAR, 1, 1)
end   = datetime.now()

# Fetch data
debt_raw = web.DataReader('REVOLSL', 'fred', start, end)  # Millions $
recession = web.DataReader('USREC', 'fred', start, end)

# Convert to trillions
debt = debt_raw / 1_000_000  # Trillions

# Inflation adjustment (real debt in latest dollars)
if INFLATION_ADJUSTED:
    cpi = web.DataReader('CPIAUCSL', 'fred', start, end)
    base_cpi = cpi.iloc[-1]['CPIAUCSL']  # Latest CPI as base
    debt_real = debt * (base_cpi / cpi['CPIAUCSL'])

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
    'legend.facecolor': '#1a1a1a',
    'legend.edgecolor': '#333333',
    'legend.fontsize':  10,
})

fig, ax = plt.subplots(figsize=(14, 7))

# Nominal debt (always shown)
ax.plot(debt.index, debt['REVOLSL'], color='#4da6ff', linewidth=1.6, label='Nominal Debt')

# Real debt (optional)
if INFLATION_ADJUSTED:
    ax.plot(debt_real.index, debt_real['REVOLSL'], color='#00ff88', linewidth=1.6, label='Real Debt (2025 $)')

# Recession shading
in_rec = False
rec_start = None
label_added = False
for date, row in recession.iterrows():
    if row['USREC'] == 1 and not in_rec:
        in_rec = True
        rec_start = date
    elif row['USREC'] == 0 and in_rec:
        in_rec = False
        lbl = 'Recession' if not label_added else ""
        ax.axvspan(rec_start, date, color='#cc4444', alpha=0.25, label=lbl)
        label_added = True
if in_rec:
    lbl = 'Recession' if not label_added else ""
    ax.axvspan(rec_start, end, color='#cc4444', alpha=0.25, label=lbl)

# Title & labels
mode = "Nominal + Real" if INFLATION_ADJUSTED else "Nominal"
latest_nominal = debt.iloc[-1]['REVOLSL']
title = f'US Credit Card / Revolving Debt ({START_YEAR}–Now)\nLatest: ${latest_nominal:.3f} trillion ({mode})'
ax.set_title(title, color='white', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('Year', color='white')
ax.set_ylabel('Outstanding Debt (Trillions $)', color='white')

ax.legend(loc='upper left', framealpha=0.95)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ———————————————— FINAL SUMMARY ————————————————
print(f"Latest Nominal Debt: ${latest_nominal:.3f} trillion")
if INFLATION_ADJUSTED:
    latest_real = debt_real.iloc[-1]['REVOLSL']
    print(f"Latest Real Debt (2025 $): ${latest_real:.3f} trillion")