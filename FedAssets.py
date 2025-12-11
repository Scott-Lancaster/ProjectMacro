#!/usr/bin/env python3
import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'

"""
===============================================================================
US FEDERAL RESERVE TOTAL ASSETS | Dark Mode
===============================================================================

WHAT IT SHOWS
  Weekly Total Assets of the Federal Reserve (Millions of USD)
  Shaded U.S. recessions (NBER)

WHY IT MATTERS
  The Federal Reserve's total assets reflect its balance sheet size, primarily 
  driven by open market operations (like Quantitative Easing/Tightening) and 
  lending facilities.
  Rapid increases often correlate with unconventional monetary policy designed
  to provide liquidity during financial crises or recessions.
  Its movements are a key indicator of monetary policy stance.

DATA SOURCES (FRED)
  WALCL:  https://fred.stlouisfed.org/series/WALCL (Total Assets)
  USREC:  https://fred.stlouisfed.org/series/USREC (Recession Indicator)

DATA FREQUENCY: Weekly, As of Wednesday (FRED update: H.4.1 Release)

ZOOM: Set START_YEAR
===============================================================================
"""

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# ———————————————— OPTIONS ————————————————
START_YEAR = 2005 # Total assets became relevant with QE after 2008
# ———————————————————————————————————————————————

start = datetime(START_YEAR, 1, 1)
end   = datetime.now()

# Fetch data
# WALCL: Assets: Total Assets: Total Assets (Less Eliminations from Consolidation): Wednesday Level (Millions of U.S. Dollars)
fed_assets = web.DataReader('WALCL', 'fred', start, end)
# USREC: U.S. Recession Indicators (Monthly)
recession = web.DataReader('USREC', 'fred', start, end)

# Rename the asset column for clarity
ASSET_SERIES = 'Total_Assets'
fed_assets = fed_assets.rename(columns={'WALCL': ASSET_SERIES})

# Convert assets from Millions of USD to Billions of USD for better plot scaling
fed_assets[ASSET_SERIES] = fed_assets[ASSET_SERIES] / 1000

# ———————————————— DATA SUMMARY ————————————————
latest_date = fed_assets.index[-1].strftime('%b %d, %Y')
latest_assets = fed_assets[ASSET_SERIES].iloc[-1]
peak_assets = fed_assets[ASSET_SERIES].max()
peak_date = fed_assets[ASSET_SERIES].idxmax().strftime('%b %d, %Y')

print("\n=== FEDERAL RESERVE TOTAL ASSETS SUMMARY ===")
print(f"Latest Reading ({latest_date}): ${latest_assets:,.2f} Billion")
print(f"Peak Reading ({peak_date}): ${peak_assets:,.2f} Billion")

# ———————————————— DARK MODE PLOT ————————————————
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 7))

# Total Assets line
ax.plot(fed_assets.index, fed_assets[ASSET_SERIES], 
        color='#4da6ff', linewidth=2.0, label='FED Total Assets')

# Recession shading (USREC is monthly, WALCL is weekly, but it works fine)
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
# Handle case where a recession is ongoing
if in_rec:
    lbl = 'Recession' if not label_added else ""
    ax.axvspan(rec_start, end, color='#cc4444', alpha=0.25, label=lbl)


# Title and Labels
ax.set_title(f'Federal Reserve Total Assets ({START_YEAR}–Now)\n'
             f'Latest: ${latest_assets:,.2f} Billion',
             color='white', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('Year', color='white')
ax.set_ylabel('Total Assets (Billions of USD)', color='white')
ax.legend(loc='upper left', framealpha=0.95)
ax.grid(True, alpha=0.3)
ax.ticklabel_format(style='plain', axis='y') # Prevent scientific notation on Y-axis
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show() # 

# ———————————————— FINAL SUMMARY ————————————————
print(f"\nLatest FED Total Assets: ${latest_assets:,.2f} Billion")
print(f"Peak Assets: ${peak_assets:,.2f} Billion on {peak_date}")