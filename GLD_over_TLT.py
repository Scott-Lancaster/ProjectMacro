#!/usr/bin/env python3

"""
===============================================================================
GLD / TLT RATIO | Dark Mode
===============================================================================

WHAT IT SHOWS
  Daily ratio = GLD (Gold ETF) ÷ TLT (Long-Term Treasury ETF)
  Shaded U.S. recessions (NBER)

WHY IT MATTERS
  Gold outperforms long bonds during:
    • Inflation fears
    • Geopolitical crises
    • Equity market stress
    • Flight-to-safety rotations
  A rising ratio signals risk-off sentiment — investors prefer gold's store-of-value over bond duration risk.
  A falling ratio suggests calm markets and confidence in fixed income.

  → A leading macro barometer for risk appetite and inflation expectations.

DATA SOURCES
  GLD:  https://finance.yahoo.com/quote/GLD   (launched Nov 2004)
  TLT:  https://finance.yahoo.com/quote/TLT   (launched Jul 2002)
  USREC: https://fred.stlouisfed.org/series/USREC

DATA FREQUENCY: Daily (market close; updated ~4:00 PM ET)

ZOOM: Auto-adapts to available data (GLD starts 2004)
===============================================================================
"""

import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'

import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import requests

# ----------------------------------------------------------------------
# 1. CONFIG – 15 years
# ----------------------------------------------------------------------
end = datetime.now()
start = end - timedelta(days=15 * 365)
fallback_start = end - timedelta(days=365)

print(f"Trying date range: {start.date()} → {end.date()}")

# ----------------------------------------------------------------------
# 2. FETCH PRICE DATA – WITH RETRY + TIMEOUT
# ----------------------------------------------------------------------
def download_price(tickers, start, end, retries=2, timeout=60):
    for attempt in range(retries + 1):
        try:
            df = yf.download(
                tickers=tickers,
                start=start,
                end=end,
                auto_adjust=False,
                progress=False,
                timeout=timeout
            )['Adj Close']
            if not df.empty:
                return df
        except Exception as e:
            print(f"  yfinance attempt {attempt+1} failed: {e}")
            time.sleep(5)
    raise RuntimeError("All yfinance attempts failed")

print("Fetching GLD & TLT from Yahoo Finance...")
price = download_price(['GLD', 'TLT'], start, end)

print(f"Raw price rows: {len(price)}")

# ---- fallback -------------------------------------------------------
if price.empty or 'GLD' not in price.columns or 'TLT' not in price.columns:
    print("15y fetch failed – trying last 1 year...")
    price = download_price(['GLD', 'TLT'], fallback_start, end)
    print(f"Fallback rows: {len(price)}")
    start = fallback_start

price = price.dropna()
print(f"Rows after dropna: {len(price)}")

if price.empty:
    ratio = pd.Series(dtype=float)
    print("ERROR: No price data – check network / yfinance")
else:
    ratio = price['GLD'] / price['TLT']
    print(f"Ratio: {len(ratio)} points | {ratio.min():.3f} – {ratio.max():.3f}")

# ----------------------------------------------------------------------
# 3. FETCH RECESSION DATA – WITH RETRY (no timeout in DataReader)
# ----------------------------------------------------------------------
def fetch_fred(series, start, end, retries=3):
    for attempt in range(retries):
        try:
            return web.DataReader(series, 'fred', start, end)  # No timeout arg
        except Exception as e:
            print(f"  FRED attempt {attempt+1} failed: {e}")
            time.sleep(10)
    raise RuntimeError("FRED download failed after retries")

print("Fetching US recession indicator from FRED...")
recession = fetch_fred('USREC', start, end)
print(f"Recession rows: {len(recession)}")

# ----------------------------------------------------------------------
# 4. PLOT
# ----------------------------------------------------------------------
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 7))

if ratio.empty:
    ax.text(0.5, 0.5,
            "NO DATA\nUpdate yfinance:\npip install --upgrade yfinance",
            transform=ax.transAxes, ha='center', va='center',
            color='red', fontsize=16)
    ax.set_title('GLD / TLT Ratio – Error', color='white')
else:
    ax.plot(ratio.index, ratio, color='#ffcc00', linewidth=2,
            label='GLD / TLT Ratio')

    in_rec = False
    rec_start = None
    label_added = False
    for ts, row in recession.iterrows():
        dt = ts.to_pydatetime()
        if dt not in ratio.index:
            continue
        if row['USREC'] == 1 and not in_rec:
            in_rec = True
            rec_start = dt
        elif row['USREC'] == 0 and in_rec:
            in_rec = False
            lbl = 'Recession' if not label_added else ""
            ax.axvspan(rec_start, dt, color='gray', alpha=0.3, label=lbl)
            label_added = True
    if in_rec:
        lbl = 'Recession' if not label_added else ""
        ax.axvspan(rec_start, ratio.index[-1], color='gray', alpha=0.3, label=lbl)

    ax.axhline(1.0, color='white', linestyle='--', linewidth=1.2, alpha=0.7)
    period = "15-Year History" if (end - start).days > 1000 else "1-Year"
    ax.set_title(f'GLD / TLT Ratio – {period}', color='white', fontsize=16, pad=15)
    ax.set_xlabel('Year', color='white')
    ax.set_ylabel('GLD / TLT', color='white')
    ax.legend(loc='upper left', framealpha=0.95)

ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(base=2))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
plt.tight_layout()
plt.show()

# ----------------------------------------------------------------------
# 5. SUMMARY
# ----------------------------------------------------------------------
if not ratio.empty:
    print(f"\nLatest GLD/TLT: {ratio.iloc[-1]:.3f}  ({ratio.index[-1].date()})")
else:
    print("\nNo data plotted.")