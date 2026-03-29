import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

# This script plots the nutrient variability. 

# Import data

all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(12, 15), dpi=600, sharex=True)


params = ["PO4",  "NO3", "NO2", "NH4", "Si"]
labels = ["PO$_4$ / μmol L⁻¹", "NO$_3$ / μmol L⁻¹", "NO$_2$ / μmol L⁻¹", "NH$_4$ / μmol L⁻¹", "Si / μmol L⁻¹"]
colors = [
    "xkcd:sea blue",
    "xkcd:sea blue",
    "xkcd:sea blue",
    "xkcd:sea blue",
    "xkcd:sea blue",

]

for i, var in enumerate(params):
    axes[i].scatter(
        all_data["datetime"],
        all_data[var],
        label=labels[i],
        zorder=10,
        color=colors[i],
        s=40,
    )
    axes[i].set_ylabel(labels[i], fontsize=17)
    # axes[i].legend(loc="upper right")
    axes[i].tick_params(axis="y", labelsize=12)
    axes[i].grid(alpha=0.25)


axes[-1].xaxis.set_major_locator(mdates.MonthLocator())  # One tick per month
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
# axes[-1].set_xlabel("Datetime", fontsize=14)
plt.xticks(rotation=45, fontsize = 15)

plt.tight_layout()
