import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator


## This script plots the High resolution sampling period (72 hours) for TA, DIC and pH

# Import data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

# Copy df
all_data2 = all_data.copy()

# Select the time frame
L = (all_data2["datetime"] >= "2022-03-29") & (all_data2["datetime"] <= "2022-04-01")
all_data2["datenum"] = mdates.date2num(all_data2["datetime"])



fig, axes = plt.subplots(3, 1, figsize=(10, 8), dpi=600, sharex=True)
parameters = [
    {
        "name": "alkalinity",
        "scatter_color": "xkcd:purple",
        "line_color": "xkcd:light purple",
        "interp_color": "xkcd:purple",
        "ylabel": "TA / μmol.kg⁻¹",
    },
    {
        "name": "dic",
        "scatter_color": "xkcd:dark blue",
        "line_color": "xkcd:water blue",
        "interp_color": "xkcd:dark blue",
        "ylabel": "DIC / μmol.kg⁻¹",
    },
    {
        "name": "pH_insitu",
        "scatter_color": "xkcd:copper",
        "line_color": "xkcd:pastel orange",
        "ylabel": "pH",
    },
]

# Dates for interpolation
interp_dates = ["2022-03-29", "2022-03-30", "2022-03-31"]

for i, param in enumerate(parameters):
    ax = axes[i]
    var = param["name"]
    
    # Highlight specific time period
    if var == "pH_insitu":
        # Define the time period to highlight
        highlight_start = pd.to_datetime("2022-03-30 15:00:00")
        highlight_end = pd.to_datetime("2022-03-30 16:00:00")
        
        # Create masks for regular and highlighted points
        highlight_mask = (
            (all_data2[L]["datetime"] >= highlight_start) & 
            (all_data2[L]["datetime"] <= highlight_end)
        )
        regular_mask = ~highlight_mask
        
        # Plot regular points in dark color
        ax.scatter(
            all_data2[L][regular_mask]["datetime"],
            all_data2[L][regular_mask][var],
            c="xkcd:dark",
            s=30,
            zorder=10,
        )
        
        # Plot highlighted points in red
        ax.scatter(
            all_data2[L][highlight_mask]["datetime"],
            all_data2[L][highlight_mask][var],
            c="red",
            s=30,
            zorder=11,  
        )
    else:
        # Regular scatter points for other parameters
        ax.scatter(
            all_data2[L]["datetime"],
            all_data2[L][var],
            c="xkcd:dark",
            s=30,
            zorder=10,
        )
    
    # Continuous data
    column_to_plot = (
        "predicted_alk_sal" if var == "alkalinity" else
        "calculated_dic" if var == "dic" else
        "pH_sensor"
    )
    ax.plot(
        all_data2[L]["datetime"],
        all_data2[L][column_to_plot],
        c="xkcd:sea blue",
        lw=2.3,
    )
    
    # Vertical lines for each day
    range_day = pd.date_range(all_data2[L]["datetime"].min(), all_data2[L]["datetime"].max(), freq="D")
    for day in range_day:
        ax.axvline(day, c='xkcd:black', ls='-', lw=1)
    
    # Making it pretty
    ax.set_ylabel(param["ylabel"], fontsize=12)
    ax.yaxis.labelpad = 15
    ax.tick_params(axis="y", which="major", labelsize=10)
    ax.grid(lw=0.8, alpha=0.7, ls="--")
    ax.text(
        0.96,  
        0.05,  
        f"({chr(97 + i)})",  
        transform=ax.transAxes,  
        fontsize=12,  
        fontweight="bold",  
        va="bottom",  
    )

# Set x-axis limits to tightly fit the data
x_min = all_data2[L]["datetime"].min()
x_max = all_data2[L]["datetime"].max()
for ax in axes:
    ax.set_xlim(x_min, x_max)

# Update the x-axis formatting for the last subplot
axes[-1].xaxis.set_major_locator(HourLocator(byhour=[0, 12])) 
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H"))
# plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()




