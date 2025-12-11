#!/usr/bin/env python3
import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'

"""
===============================================================================
S&P 500 PRICED IN GOLD | Dark Mode
===============================================================================

WHAT IT SHOWS
  Daily S&P 500 Index ÷ Gold ETF Price (SPX points per GLD share)
  Shaded U.S. recessions (NBER)

WHY IT MATTERS
  Removes dollar illusion — shows true relative performance.
  Falling ratio = gold winning (risk-off, crisis, inflation hedge)
  Rising ratio = stocks winning (risk-on, growth)
  Major lows often mark equity bear market bottoms (2008, 2020)

DATA SOURCES
  ^GSPC: Yahoo Finance (S&P 500)
  GLD:   Yahoo Finance (SPDR Gold ETF proxy for gold price)
  USREC: FRED recession indicator

ZOOM: Set START_YEAR (data starts 2004 for GLD)
===============================================================================
"""

import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime

# ———————————————— ZOOM SETTINGS ————————————————
START_YEAR = 2004  # GLD starts Nov 2004
# ———————————————————————————————————————————————

start = datetime(START_YEAR, 1, 1)
end   = datetime.now()

try:
    # Fetch S&P 500
    print("Fetching S&P 500 from Yahoo Finance...")
    spx = yf.download(
        '^GSPC',
        start=start,
        end=end,
        auto_adjust=False,
        progress=False
    )['Adj Close']

    # Fetch Gold ETF (GLD — daily proxy for gold price)
    print("Fetching Gold ETF (GLD) from Yahoo Finance...")
    gld = yf.download(
        'GLD',
        start=start,
        end=end,
        auto_adjust=False,
        progress=False
    )['Adj Close']

    # Combine and compute ratio
    data = pd.concat([spx, gld], axis=1).dropna()
    data.columns = ['SPX', 'GLD']
    data['SPX_in_Gold'] = data['SPX'] / data['GLD']  # SPX points per GLD share (proxy for oz gold)

    ratio = data['SPX_in_Gold']

    if ratio.empty:
        raise ValueError("No overlapping data — try a shorter date range")

    # Recession data
    recession = web.DataReader('USREC', 'fred', start, end)

    # ———————————————— DARK MODE PLOT ————————————————
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(ratio.index, ratio, color='#4da6ff', linewidth=1.6, label='S&P 500 Priced in Gold')

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
    ax.set_title(f'S&P 500 Priced in Gold ({START_YEAR}–Now)\n'
                 f'Latest: {ratio.iloc[-1]:.1f} SPX points per GLD share',
                 color='white', fontsize=14, pad=20, fontweight='bold')
    ax.set_xlabel('Year', color='white')
    ax.set_ylabel('SPX / GLD (points per share)', color='white')

    ax.legend(loc='upper left', framealpha=0.95)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Summary
    latest_ratio = ratio.iloc[-1]
    print(f"\nLatest S&P 500 in Gold: {latest_ratio:.1f} points per GLD share")
    print("Interpretation: Lower = gold stronger vs stocks | Higher = stocks stronger vs gold")

except Exception as e:
    print(f"Error: {e}")
    print("Try: pip install --upgrade yfinance pandas-datareader")