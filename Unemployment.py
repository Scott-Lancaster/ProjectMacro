#!/usr/bin/env python3
import os
os.environ['MATPLOTLIB_NO_SECURE_CODING_WARNING'] = '1'

"""
===============================================================================
US UNEMPLOYMENT RATE + SAHM RULE | Dark Mode
===============================================================================

WHAT IT SHOWS
  Monthly US unemployment rate (%)
  Shaded U.S. recessions (NBER)
  Optional red dots = Sahm Rule triggered (3MMA ≥ +0.5 pp from 12-month low)

WHY IT MATTERS
  The Sahm Rule has predicted every U.S. recession since 1970 with zero false positives.
  It signals accelerating job losses — a confirming recession indicator.
  Current status: Safe / Near Trigger / Triggered

DATA SOURCES (FRED)
  UNRATE: https://fred.stlouisfed.org/series/UNRATE
  USREC:  https://fred.stlouisfed.org/series/USREC

DATA FREQUENCY: Monthly (BLS release: 1st Friday ~8:30 AM ET | FRED update: +1–3 days)

ZOOM: Set START_YEAR
===============================================================================
"""

import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ———————————————— OPTIONS ————————————————
START_YEAR = 1950
SHOW_SAHM_DOTS = False   # Set to False to hide Sahm trigger dots
# ———————————————————————————————————————————————

start = datetime(START_YEAR, 1, 1)
end   = datetime.now()

# Fetch data
unrate = web.DataReader('UNRATE', 'fred', start, end)
recession = web.DataReader('USREC', 'fred', start, end)

# ———————————————— SAHM RULE ————————————————
unrate['3MMA'] = unrate['UNRATE'].rolling(3).mean()
unrate['12M_Low'] = unrate['3MMA'].rolling(12).min().shift(1)
unrate['Sahm_Rule'] = unrate['3MMA'] - unrate['12M_Low']
unrate['Sahm_Trigger'] = unrate['Sahm_Rule'] >= 0.5

triggers = unrate[unrate['Sahm_Trigger']].dropna()

# Current Sahm status
current_sahm = unrate['Sahm_Rule'].iloc[-1]
current_unrate = unrate['UNRATE'].iloc[-1]
status = "TRIGGERED" if current_sahm >= 0.5 else "Near Trigger" if current_sahm >= 0.35 else "Safe"

# ———————————————— PRINT LAST 4 SAHM READINGS ————————————————
print("\n=== LAST 4 SAHM RULE READINGS (Date | Unemployment | 3MMA | Sahm Rise) ===")
last_4 = unrate[['UNRATE', '3MMA', 'Sahm_Rule']].tail(4)
for date, row in last_4.iterrows():
    print(f"{date.strftime('%b %Y')}: {row['UNRATE']:.1f}% | 3MMA = {row['3MMA']:.2f} | Sahm = {row['Sahm_Rule']:.2f} pp")

if last_4.index[-1] < datetime.now() - timedelta(days=45):
    print("(Note: Data may be stale — FRED lags after BLS releases)")

# ———————————————— DARK MODE PLOT ————————————————
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 7))

# Unemployment line
ax.plot(unrate.index, unrate['UNRATE'], color='#4da6ff', linewidth=1.4, label='Unemployment Rate')

# Optional Sahm trigger dots (no label on last one)
if SHOW_SAHM_DOTS and not triggers.empty:
    ax.scatter(triggers.index, triggers['UNRATE'], color='#ff4444', s=80, zorder=5,
               edgecolors='white', linewidth=1, label='Sahm Rule Trigger')

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

# Title
ax.set_title(f'US Unemployment Rate + Sahm Rule ({START_YEAR}–Now)\n'
             f'Latest: {current_unrate:.2f}% | Sahm: {current_sahm:.2f} pp → {status}',
             color='white', fontsize=14, pad=20, fontweight='bold')
ax.set_xlabel('Year', color='white')
ax.set_ylabel('Unemployment Rate (%)', color='white')
ax.legend(loc='upper left', framealpha=0.95)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(2))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ———————————————— FINAL SUMMARY ————————————————
print(f"\nLatest Unemployment: {current_unrate:.2f}%")
print(f"Sahm Rule: {current_sahm:.2f} pp → {status}")
if not triggers.empty:
    last = triggers.iloc[-1]
    print(f"Last Sahm Trigger: {last.name.strftime('%B %Y')} ({last['Sahm_Rule']:.2f} pp)")
else:
    print("No Sahm triggers in this period")