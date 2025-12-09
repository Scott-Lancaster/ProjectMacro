# utils/plotting.py
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_chart(
    data_series,
    title,
    ylabel,
    start_date,
    end_date,
    recession_data=None,
    reference_line=None,
    color='#ffcc00',
    period_label="History"
):
    """
    Universal dark-mode plotter for macro charts.
    
    Parameters:
    - data_series: pd.Series with DatetimeIndex
    - title: str
    - ylabel: str
    - start_date, end_date: datetime
    - recession_data: pd.DataFrame with 'USREC' (optional)
    - reference_line: float (e.g., 1.0 or 0.0)
    - color: line color
    - period_label: "15-Year", "30-Day", etc.
    """
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor' : '#0a0a0a',
        'axes.facecolor'   : '#0a0a0a',
        'axes.edgecolor'   : '#333333',
        'axes.labelcolor'  : 'white',
        'text.color'       : 'white',
        'xtick.color'      : 'white',
        'ytick.color'      : 'white',
        'grid.color'       : '#2a2a2a',
        'grid.alpha'       : 0.3,
        'legend.facecolor' : '#1a1a1a',
        'legend.edgecolor' : '#333333',
        'legend.fontsize'  : 10,
    })

    fig, ax = plt.subplots(figsize=(14, 7))

    # Main line
    ax.plot(data_series.index, data_series, color=color, linewidth=2, label=ylabel)

    # Recession shading
    if recession_data is not None:
        in_rec = False
        rec_start = None
        label_added = False
        for ts, row in recession_data.iterrows():
            dt = ts.to_pydatetime()
            if dt not in data_series.index:
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
            ax.axvspan(rec_start, data_series.index[-1], color='gray', alpha=0.3, label=lbl)

    # Reference line (e.g., 1.0 or 0.0)
    if reference_line is not None:
        ax.axhline(reference_line, color='white', linestyle='--', linewidth=1.2, alpha=0.7)

    # Title & labels
    ax.set_title(f'{title} – {period_label}', color='white', fontsize=16, pad=15)
    ax.set_xlabel('Year', color='white')
    ax.set_ylabel(ylabel, color='white')

    # Legend
    ax.legend(loc='upper left', framealpha=0.95)

    # Grid
    ax.grid(True, alpha=0.3)

    # X-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(base=2))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.show()