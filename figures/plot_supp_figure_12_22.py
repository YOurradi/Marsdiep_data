import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# This script plots the river discharges for figure 12 and 22 in supplementary information.


# Year 2022-2023
data_ijssel = pd.read_csv("Marsdiep_data/data/discharge_data/LakeIJssel_Q_2022_2023.dat", 
                         delim_whitespace=True,  skiprows=1)

data_ijssel = data_ijssel.drop(index=0).reset_index(drop=True)
data_ijssel["Date"] = pd.to_datetime(data_ijssel["Date"])
data_ijssel = data_ijssel.sort_values("Date")
data_ijssel["Discharge"] = pd.to_numeric(data_ijssel["Discharge"], errors="coerce")

data_rhine = pd.read_csv("Marsdiep_data/data/discharge_data/Rhine_Q_2022_2023.dat", 
                         delim_whitespace=True,  skiprows=1)
data_rhine = data_rhine.drop(index=0).reset_index(drop=True)
data_rhine["Date"] = pd.to_datetime(data_rhine["Date"])
data_rhine = data_rhine.sort_values("Date")
data_rhine["Discharge"] = pd.to_numeric(data_rhine["Discharge"], errors="coerce")
data_rhine.loc[data_rhine["Discharge"] < 0, "Discharge"] = np.nan

data_ijssel = pd.read_csv("Marsdiep_data/data/discharge_data/Lake_IJssel_Q_2001_2024.dat",
                          sep=r"\s+", skiprows=1, engine="python").drop(index=0).reset_index(drop=True)

data_rhine = pd.read_csv("Marsdiep_data/data/discharge_data/Rhine_Q_2001_2024.dat",
                         sep=r"\s+", skiprows=1, engine="python").drop(index=0).reset_index(drop=True)


data_ijssel["Year"] = pd.to_datetime(data_ijssel["Year"], errors="coerce").dt.year
data_ijssel["Discharge"] = pd.to_numeric(data_ijssel["Discharge"], errors="coerce")
data_rhine["Year"]  = pd.to_datetime(data_rhine["Year"], errors="coerce").dt.year
data_rhine["Discharge"] = pd.to_numeric(data_rhine["Discharge"], errors="coerce")


def simple_trend(x, y):
    ok = (~np.isnan(x)) & (~np.isnan(y))
    x_ok = x[ok]
    y_ok = y[ok]
    if len(x_ok) < 2:
        return None, None, None
    slope, intercept = np.polyfit(x_ok, y_ok, 1)
    yhat = slope * x + intercept
    # compute R^2 safely
    ss_res = np.nansum((y_ok - (slope * x_ok + intercept))**2)
    ss_tot = np.nansum((y_ok - np.nanmean(y_ok))**2)
    r2 = 1 - ss_res/ss_tot if ss_tot != 0 else np.nan
    return slope, intercept, r2

# Plotting supplementary figure 12
fig, ax = plt.subplots(figsize=(15,8),dpi=600)

ax.plot(
    data_ijssel["Date"],
    data_ijssel["Discharge"],
    # s=10,
    c="xkcd:light blue",
    lw=2.4,
    zorder=10,
    label="Lake IJssel"
)

ax.plot(
    data_rhine["Date"],
    data_rhine["Discharge"],
    # s=10,
    c="xkcd:blueberry",
    lw=2.4,
    label="Rhine"
)


# format x-axis: show Month-Year
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))  
ax.set_ylim(-20,3200)
# plt.xticks(rotation=45)
plt.ylabel("Discharge / m³.s⁻¹", fontsize=19, labelpad=15)
ax.tick_params(axis="both", which="major", labelsize=15)
ax.grid(alpha=0.25, ls="--")
ax.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=17 ,frameon=False )

# Plotting supplementary figure 22

fig, ax = plt.subplots(figsize=(17,8), dpi=600)

# IJssel
ax.plot(data_ijssel["Year"], data_ijssel["Discharge"], c="xkcd:light blue", lw=3.5, zorder=10, label="Lake IJssel")
ax.scatter(data_ijssel["Year"], data_ijssel["Discharge"], c="xkcd:light blue", zorder=10, s=15)
s_i, b_i, r2_i = simple_trend(data_ijssel["Year"].values, data_ijssel["Discharge"].values)
if s_i is not None:
    ax.plot(data_ijssel["Year"], s_i * data_ijssel["Year"] + b_i, linestyle="--", linewidth=2,
            color="xkcd:light blue")

# Rhine
ax.plot(data_rhine["Year"], data_rhine["Discharge"], c="xkcd:blueberry", lw=3.5, alpha=0.9, label="Rhine")
ax.scatter(data_rhine["Year"], data_rhine["Discharge"], c="xkcd:blueberry", s=15)
s_r, b_r, r2_r = simple_trend(data_rhine["Year"].values, data_rhine["Discharge"].values)
if s_r is not None:
    ax.plot(data_rhine["Year"], s_r * data_rhine["Year"] + b_r, linestyle="--", linewidth=2,
            color="xkcd:blueberry")

# formatting
ax.set_xticks(np.unique(data_ijssel["Year"].dropna().astype(int)[::2]))
ax.set_xticklabels(np.unique(data_ijssel["Year"].dropna().astype(int)[::2]), fontsize=14)
plt.ylabel("Discharge / m³.y⁻¹", fontsize=24, labelpad=10)
ax.tick_params(axis="both", which="major", labelsize=20)
ax.grid(alpha=0.25, ls="--")
ax.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=18, frameon=False)
plt.tight_layout()

