import pandas as pd, numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import least_squares
import PyCO2SYS as pyco2
from scipy.stats import wasserstein_distance

# This script plots and calcualtes the wasserstein distance

# Import data

all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

data = all_data.copy()
data["date"] = data["datetime"].dt.date

# calculate daily averages
params = ["salinity", "water_level", "water_level_diff", "pH_sensor", "temperature"]

avg = data.groupby("date")[params].mean().reset_index()
data = pd.merge(data, avg, on="date", how="left", suffixes=("", "_avg_day"))
data["doy"] = data["datetime"].dt.dayofyear


def predict_alk(alk_coefficient, salinity, dayofyear, water_level, water_level_diff):
    """predic alkalinity from salinity"""
    slope, intercept, msin, mcos, offset, mwater, mwdiff = alk_coefficient
    alkalinity = (
        slope * salinity
        + intercept
        + msin * np.sin(((dayofyear - offset) * 2 * np.pi) / 365)
        + mcos * np.cos(((dayofyear - offset) * 2 * np.pi) / 365)  
        + mwater * water_level
        + mwdiff * water_level_diff
        #+ mwdiff * (water_level_diff**3)  - (slope * water_level_diff) 
    )
    return alkalinity

L = (
    data.alkalinity.notnull()
    & data.water_level.notnull()
    & data.water_level_diff.notnull()
)


def _lsqfun_predict_alk(
    alk_coefficient, salinity, dayofyear, water_level, water_level_diff, true_alk
):
    return (
        predict_alk(alk_coefficient, salinity, dayofyear, water_level, water_level_diff)
        - true_alk
    )

opt_results = least_squares(
    _lsqfun_predict_alk,
    [-6, 2600, 50, -2, 0, 0, 0],
    args=(
        data[L].salinity,
        data[L].datetime.dt.dayofyear,
        data[L].water_level,
        data[L].water_level_diff,
        data[L].alkalinity,
    ),
)
data["predicted_alk_sal_avg"] = predict_alk(
    opt_results["x"],
    data.salinity_avg_day,
    data.datetime.dt.dayofyear,
    data.water_level_avg_day,
    data.water_level_diff_avg_day,
)

# DIC_tot is : calculated_dic

# Recalculate the dic using the avg data

# DIC_bio
results = pyco2.sys(
    par1=data.pH_sensor,
    par2=data.predicted_alk_sal_avg,
    par1_type=3,
    par2_type=1,
    # temperature = all_data.temperature.values,
    temperature=data.temperature_avg_day.values,
    salinity=data.salinity_avg_day.values,
)

data["dic_bio"] = results["dic"]

# DIC_hydro
results = pyco2.sys(
    par1=data.pH_sensor_avg_day,
    par2=data.predicted_alk_sal,
    par1_type=3,
    par2_type=1,
    # temperature = all_data.temperature.values,
    temperature=data.temperature.values,
    salinity=data.salinity.values,
)

data["dic_hydro"] = results["dic"]

# Calculate dic_bio_tot
data["dic_bio_tot"] = data["dic_bio"] - data["calculated_dic"]

# Calculate dic_hydro_tot
data["dic_hydro_tot"] = data["dic_hydro"] - data["calculated_dic"]


def calculate_wasserstein_bio(group):

    L = group["dic_bio"].notnull() & group["calculated_dic"].notnull()
    u = group.loc[L, "calculated_dic"]
    v = group.loc[L, "dic_bio"]
    
    if u.empty or v.empty:   
        return np.nan           

    return wasserstein_distance(u, v)


wasserstein_bio = data.groupby("date").apply(calculate_wasserstein_bio)


def calculate_wasserstein_hydro(group):

    L = group["dic_bio"].notnull() & group["calculated_dic"].notnull()
    u = group.loc[L, "calculated_dic"]
    v = group.loc[L, "dic_hydro"]
    
    if u.empty or v.empty:   
        return np.nan   

    return wasserstein_distance(u, v)


wasserstein_hydro = data.groupby("date").apply(calculate_wasserstein_hydro)

# PLotting
fig, ax = plt.subplots(dpi=600, figsize=(6,3))

(100 * wasserstein_hydro / (wasserstein_hydro + wasserstein_bio)).plot(
    ax=ax, c="xkcd:sea blue", lw=1.4) 

ax.set_ylim(0, 100)
ax.set_ylabel("Wasserstein distance  ""%" , fontsize=8)
ax.set_xlabel("")  # Remove the x-axis label (or set a custom label)
ax.tick_params(axis="both", which="major", labelsize=7)
plt.grid(alpha=0.25)

current_xlim = ax.get_xlim()
ax.set_xlim(left=current_xlim[0], right=pd.Timestamp("2023-02-15"))

date1 = pd.Timestamp("2023-01-12")
date2 = pd.Timestamp("2023-01-12")
# Add annotations with subscripts
ax.text(
    date1,90, r"$\mathrm{DIC_{bio}}$",
    fontsize=8, color="black", ha="left", va="bottom"
)

ax.text(
    date2,5, r"$\mathrm{DIC_{hydro}}$",
    fontsize=8, color="black", ha="left", va="bottom"
)

ax.annotate(
    "", 
    xy=(pd.Timestamp("2023-01-20"), 88),   
    xytext=(pd.Timestamp("2023-01-20"), 13),  
    arrowprops=dict(
        arrowstyle="<->",    
        color="black",
        lw=1.9,              
        shrinkA=0, shrinkB=0,
        alpha=1.0
    )
)

plt.tight_layout()
    


