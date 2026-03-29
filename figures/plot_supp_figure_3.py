import pandas as pd
import matplotlib.pyplot as plt
import PyCO2SYS as pyco2
import numpy as np
from scipy.stats import pearsonr,linregress

# This script calcualte the organic alkalinity.

data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

results = pyco2.sys(
    par1=data.pH_insitu,
    par2=data.dic,  
    par1_type=3,
    par2_type=2,
    # temperature = all_data.temperature.values,
    temperature=data.temperature.values,
    salinity=data.salinity.values,
)

data["calculated_ta"] = results["alkalinity"]

temp_uncertainty = 0.2  
sal_uncertainty = 0.01
dic_uncer = 2
results_with_uncertainty = pyco2.sys(
    par1=data["pH_insitu"],
    par2=data.dic,
    par1_type=3,  
    par2_type=2,
    temperature=data.temperature,
    salinity=data.salinity,
    uncertainty_into=['alkalinity'],  
    uncertainty_from={
        'par1': data.uncertainty, 
        'par2' : 2 ,  #umol kg-1              
        'temperature': temp_uncertainty,  
        'salinity': sal_uncertainty * data.salinity  
    }
)

data["calculated_ta_uncertainty"] = results_with_uncertainty['u_alkalinity']


data["ta_residual"] = data["predicted_alk_sal"] - data["alkalinity"]

data["org_alk"] = data["alkalinity"] - data["calculated_ta"]

data["org_alk_unc"] = np.sqrt((1.7**2) +  data["calculated_ta_uncertainty"]**2)

# Plottting
fig, (ax1, ax2) = plt.subplots(2, 1, dpi=600, figsize=(10, 10))

ax1.scatter(data.org_alk, data.ta_residual, s=25, c="xkcd:sea blue")
ax1.set_ylabel("TA - TA$_{calc}$ / µmol kg⁻¹", fontsize=15)
ax1.set_xlabel("TA$_{res}$ / µmol kg⁻¹", fontsize=15)

L1 = data[["org_alk", "ta_residual"]].notna().all(axis=1)
r_orgalk_res, p_orgalk_res = pearsonr(data.loc[L1, "ta_residual"], data.loc[L1, "org_alk"])
r2_orgalk_res = r_orgalk_res**2

slope1, intercept1, _, _, _ = linregress(data.loc[L1, "org_alk"], data.loc[L1, "ta_residual"])
x_line1 = np.linspace(data.loc[L1, "org_alk"].min(), data.loc[L1, "org_alk"].max(), 100)
y_line1 = slope1 * x_line1 + intercept1
ax1.plot(x_line1, y_line1, c="black", linewidth=1.7)
ax1.text(0.02, 0.95, f'R² = {r2_orgalk_res:.3f}', transform=ax1.transAxes, 
         fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='none', edgecolor='none',alpha=0.8))

ax1.tick_params(axis='both', labelsize=12)
ax1.grid(alpha=0.3)


ax2.scatter(data.salinity, data.ta_residual, s=25, c="xkcd:sea blue")
ax2.set_ylabel("TA - TA$_{calc}$ / µmol kg⁻¹", fontsize=15)
ax2.set_xlabel("Salinity", fontsize=15)

mask2 = data[["org_alk", "salinity"]].notna().all(axis=1)
r_orgalk_sal, p_orgalk_sal = pearsonr(data.loc[mask2, "org_alk"], data.loc[mask2, "salinity"])
r2_orgalk_sal = r_orgalk_sal**2

slope2, intercept2, _, _, _ = linregress(data.loc[mask2, "salinity"], data.loc[mask2, "ta_residual"])
x_line2 = np.linspace(data.loc[mask2, "salinity"].min(), data.loc[mask2, "salinity"].max(), 100)
y_line2 = slope2 * x_line2 + intercept2
ax2.plot(x_line2, y_line2, c="black", linewidth=1.7)
ax2.text(0.02, 0.95, f'R² = {r2_orgalk_sal:.3f}', transform=ax2.transAxes, 
         fontsize=14, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='none',edgecolor='none', alpha=0.8))

ax2.tick_params(axis='both', labelsize=12)
ax2.grid(alpha=0.2)

plt.tight_layout()


