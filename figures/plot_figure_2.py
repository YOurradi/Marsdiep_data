import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# This script plots the pH sensor values, calibrated and uncalibrated values.

# Import data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")
daily_mean = all_data.groupby(pd.Grouper(key='datetime', freq='D'))['pH_insitu'].mean().reset_index()

fig, ax= plt.subplots(figsize= (6,3), dpi=300)

ax.scatter(
    all_data.datetime,
    all_data.pH,
    c="xkcd:marine blue",
    s=0.8)

ax.scatter(
    all_data.datetime,
    all_data.pH_sensor,
    # c="xkcd:grey",
    c="xkcd:grey blue",
    s=0.8,
    )

ax.scatter(
    daily_mean.datetime,
    daily_mean.pH_insitu,
    # c="xkcd:dark grey",
    c="xkcd:dark",
    s=8)

ax.set_ylabel("pH", fontsize=8, labelpad=3)
ax.grid(alpha=0.25, ls="-")
ax.tick_params(axis="both", labelsize=6.5)


scatter_size = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='xkcd:marine blue', markersize=5, label="Raw pH sensor"),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='xkcd:grey blue', markersize=5, label="Corrected pH sensor"),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='xkcd:dark', markersize=5, label='Measured pH')
]

plt.legend(
    handles=scatter_size,
    fontsize=6.7,             
    frameon=False            
)

plt.tight_layout()  

