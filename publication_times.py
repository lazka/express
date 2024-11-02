import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import matplotlib.dates as mdates


def gmt_to_vienna(date_gmt):
    dt = datetime.strptime(date_gmt, "%Y-%m-%dT%H:%M:%S")
    utc_dt = dt.replace(tzinfo=timezone.utc)
    vienna_dt = utc_dt.astimezone(ZoneInfo("Europe/Vienna"))
    vienna_local_dt = vienna_dt.replace(tzinfo=None)
    return vienna_local_dt


def plot_article_publication_times(dates):
    if not isinstance(dates, pd.DataFrame):
        df = pd.DataFrame({'published_at': dates})
    else:
        df = dates.copy()

    # Extract time and date components
    df['hours'] = df['published_at'].dt.hour + df['published_at'].dt.minute/60.0
    df['date'] = pd.to_datetime(df['published_at'].dt.date)

    # Create the plot
    fig, ax = plt.subplots(figsize=(20, 10))
    
    # Create 2D histogram
    h = plt.hist2d(mdates.date2num(df['date']),
                   df['hours'],
                   bins=(200, 48),
                   cmap='viridis',
                   norm=matplotlib.colors.LogNorm())
    
    # Add colorbar
    cbar = plt.colorbar(h[3], label='Number of articles')
    cbar.ax.tick_params(labelsize=10)
    
    # Format x-axis
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    
    # Format y-axis
    ax.yaxis.set_major_locator(plt.MultipleLocator(2))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
    
    # Add grids
    # Vertical lines for years (black, solid)
    ax.grid(True, which='major', axis='x', color='black', linestyle='-', linewidth=1.5, alpha=0.5)
    # Vertical lines for months (black, dashed)
    ax.grid(True, which='minor', axis='x', color='black', linestyle='--', linewidth=0.5, alpha=0.2)
    # Horizontal lines for hours (black, dashed)
    ax.grid(True, which='major', axis='y', color='black', linestyle='--', linewidth=0.5, alpha=0.3)
    
    # Customize labels and title
    plt.ylabel('Time of Day (24-hour format)', fontsize=12)
    plt.xlabel('Publication Date', fontsize=12)
    plt.title('Article Publication Times Distribution', fontsize=14, pad=20)
    
    # Add hour labels
    hour_labels = [f'{h:02d}:00' for h in range(0, 24, 2)]
    plt.yticks(range(0, 24, 2), hour_labels)
    
    # Rotate x-axis labels
    plt.xticks(rotation=0)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save with high DPI
    plt.savefig('article_publication_times.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()


def main(filename):
    with open(filename, 'r') as f:
        posts = json.load(f)

    timestamps = []
    for post in posts:
        timestamps.append(gmt_to_vienna(post['date_gmt']))

    plot_article_publication_times(timestamps)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
    else:
        main(sys.argv[1])
