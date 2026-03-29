import pandas as pd, numpy as np
import PyCO2SYS as pyco2
from scipy.optimize import least_squares
from scipy.interpolate import pchip
import calkulate as calk
from matplotlib import pyplot as plt


# Import data

all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")


no_value = all_data.copy()

# The second half only
# no_value.loc[
#     (no_value["datetime"] >= "2022-03-31") & (no_value["datetime"] <= "2022-04-01"),
#     "pH_insitu",
# ] = np.nan

# Only one value

no_value.loc[
((no_value["datetime"] >= "2022-03-29")& (no_value["datetime"] < "2022-03-30 12:00:00"))
 | ((no_value["datetime"] >= "2022-03-30 23:00:00") & (no_value["datetime"] <= "2022-04-01")),"pH_insitu"] = np.nan

#%% The calibration part

### Convert the pH sensor mv values to pH

# # Add temp_kelvin and pH_mV converted to volts
# all_data["temperature_K"] = all_data.temperature + 273.15
# all_data["pH_V"] = all_data.pH_mV / 1000

# Initial guess of emf0
emf0 = -80

L = ~no_value.pH_insitu.isnull()

def _lsqfun_convert_emf_to_pH(emf0, emf, temperature, pH):
    return calk.convert.emf_to_pH(emf, emf0, temperature) - pH

opt_results = least_squares(
    _lsqfun_convert_emf_to_pH,
    emf0,
    args=(
        no_value[L].pH_mV.values,
        no_value[L].temperature.values,
        no_value[L].pH_insitu.values,
    ),
)

no_value["pH_converted"] = calk.convert.emf_to_pH(
    no_value.pH_mV, opt_results["x"], no_value.temperature
)

no_value["emf0"] = (
    -np.log(10 ** (-no_value["pH_insitu"]))
    * ((8.3144621 * no_value.temperature_K) / 96.4853365)
    + no_value.pH_mV
)
no_value["pH_check"] = calk.convert.emf_to_pH(
    no_value.pH_mV, no_value.emf0, no_value.temperature
)

### PCHIP interpolation for the emf0

L = ~no_value["pH_insitu"].isnull()
# L2 = ~all_data["emf0"].isnull()
y = no_value.loc[L, "emf0"]
x = no_value.loc[L, "datenum"]

# Sort the values of x, and ybased on x
sort_indices = x.argsort()
y = y.iloc[sort_indices]
x = x.iloc[sort_indices]
pchip_function = pchip(x, y, extrapolate=False)

emf0_interp = pchip_function(no_value["datenum"])
no_value["emf0_interp"] = emf0_interp

### Use interpolated emf0 to calculate the pH from sensor every 10mn

no_value["pH_sensor_no_value"] = calk.convert.emf_to_pH(
    no_value["pH_mV"], no_value["emf0_interp"], no_value["temperature"]
)

results = pyco2.sys(
    par1=no_value.pH_sensor_no_value,
    par2=no_value.predicted_alk_sal,  # alk from salinity and sin function whole data
    par1_type=3,
    par2_type=1,
    # temperature = all_data.temperature.values,
    temperature=no_value.temperature.values,
    salinity=no_value.salinity.values,
)

no_value["calculated_dic_no_value"] = results["dic"]

### Calculate the dic_calc difference for the worst case scenario which is : no value

L = (no_value["datetime"] >= "2022-03-29") & (no_value["datetime"] <= "2022-04-01")

diff = (no_value["calculated_dic_no_value"] - all_data["calculated_dic"])

#%% Plotting
L = (no_value["datetime"] >= "2022-03-29") & (no_value["datetime"] <= "2022-04-01")
days = no_value[L]["datetime"].dt.floor("D").unique()
fig = plt.figure(figsize=(10,8), dpi=600)
gs = fig.add_gridspec(2, 1)

# First subplot - DIC data
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(
    no_value[L]["datetime"],
    no_value[L]["calculated_dic_no_value"],
    color="xkcd:raspberry",
    label="DIC_calc no pH value",
    lw=1.9
)
ax1.plot(
    all_data[L]["datetime"],
    all_data[L]["calculated_dic"],
    color="xkcd:sea blue",
    label="DIC_calc",
    lw=1.9,
)
ax1.scatter(
    all_data[L]["datetime"],
    all_data[L]["dic"],
    color="xkcd:black",
    s=40,
    zorder=10,
    label="DIC_meas",
)
ax1.set_ylabel("DIC / μmol.kg⁻¹", fontsize=14)
ax1.yaxis.labelpad = 15
ax1.tick_params(axis="both", which="major", labelsize=12)
plt.xticks(rotation=45)
ax1.grid(True, linewidth=0.8, alpha=0.7, linestyle="--")
for day in days:
    ax1.axvline(x=day, color="xkcd:black", ls="--", lw=1.5)

# Set x-axis limits to match data range exactly
ax1.set_xlim(no_value[L]["datetime"].min(), no_value[L]["datetime"].max())

# Second subplot - pH data (without twin axis)
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(
    no_value[L]["datetime"],
    no_value[L]["pH_sensor_no_value"],
    color="xkcd:raspberry",
    lw=1.9,
    label="pH recalibrated",
)
ax2.plot(
    all_data[L]["datetime"],
    all_data[L]["pH_sensor"],
    color="xkcd:sea blue",
    lw=1.9,
    label="pH recalibrated",
)
ax2.scatter(
    all_data[L]["datetime"],
    all_data[L]["pH_insitu"],
    color="xkcd:black",
    label="pH insitu one value",
    zorder=10,
    s=40, 
)
ax2.scatter(
    no_value[L]["datetime"],
    no_value[L]["pH_insitu"],
    color="xkcd:red",
    label="pH insitu one value",
    zorder=10,
    s=50, 
)

ax2.set_ylabel("pH", fontsize=14)
ax2.yaxis.labelpad = 15
ax2.tick_params(axis="both", which="major", labelsize=12)
plt.xticks(rotation=45)
ax2.grid(True, linewidth=0.8, alpha=0.7, linestyle="--")
for day in days:
    ax2.axvline(x=day, color="xkcd:black", ls="--", lw=1.5)


# Set x-axis limits to match data range exactly
ax2.set_xlim(no_value[L]["datetime"].min(), no_value[L]["datetime"].max())

ax1.text(0.98, 0.02, '(a)', transform=ax1.transAxes, 
         fontsize=14, fontweight='bold', va='bottom', ha='right')

ax2.text(0.98, 0.02, '(b)', transform=ax2.transAxes, 
         fontsize=14, fontweight='bold', va='bottom', ha='right')

plt.tight_layout()

