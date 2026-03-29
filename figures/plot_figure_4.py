import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

## This script plots the seasonal variation of Temperature, salinity, TA, DIC, pH, fCO₂
# and FCO₂

# Import data

all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

start = "2022-07-15 06:00:00"
end = "2022-07-22 14:00:00"
values = (
    (all_data["datetime"] >= start)
    & (all_data["datetime"] <= end)
    & (all_data["salinity"] < 29)
)

all_data.loc[values, "salinity"] = np.nan

daily_mean = all_data.groupby(pd.Grouper(key='datetime', freq='D')).mean(numeric_only=True).reset_index()

cutoff_date = pd.to_datetime('2023-01-11 10:00:00')
all_data.loc[all_data['datetime'] > cutoff_date, :] = np.nan


fig, axes = plt.subplots(nrows=7, ncols=1, figsize=(12, 15), dpi=400, sharex=True)


params = ["temperature", "salinity", "alkalinity", "pH_insitu",
          "dic", "delta_interp1d", "F_Ni00"]

labels = ["Temperature / °C", "Salinity", "TA / μmol kg⁻¹",
          "pH$_T$", "DIC / μmol kg⁻¹", "∆fCO₂ / μatm", "FCO₂ / g-C m⁻² d⁻¹"]

part_1 = {
    "temperature" : ("Temperature","xkcd:red"),
    "salinity" : ("Salinity","xkcd:tree green"),
    "delta_interp1d" : ("ΔpCO₂ / μatm","xkcd:violet red"),
    "F_Ni00" : ("FCO₂ / gC.m⁻².d⁻¹","xkcd:seafoam blue"),   
    }


part_2 = {
    "alkalinity" : ("Alkalinity / μmol.kg⁻¹","xkcd:purple"),
    "pH_insitu" : ("pH","xkcd:copper"),
    "dic" : ("DIC /μmol kg⁻¹","xkcd:dark blue"),
    }

part_3 ={
    "alkalinity": ("predicted_alk_sal", "xkcd:light purple"),
    "pH_insitu": ("pH_sensor", "xkcd:pastel orange"),
    "dic": ("calculated_dic", "xkcd:water blue") 
    }
params = ["temperature", "salinity", "alkalinity", "pH_insitu", 
          "dic", "delta_interp1d", "F_Ni00"]

letters = ["a","b","c","d","e","f","g"]

for i, var in enumerate(params):

    if var in part_1:
        label, color = part_1[var]
        axes[i].scatter(
            all_data["datetime"],
            all_data[var],
            label=f"Measured {label}",
            # c=color,
            color="xkcd:sea blue",  # dark grey
            s=1,
            alpha=0.5,   # reduce the alpha and try it
            # edgecolor=None
        )
        
    # if var in part_2:
    #     label, color = part_2[var]
    #     axes[i].scatter(
    #         all_data["datetime"],
    #         all_data[var],
    #         label=f"Measured {label}",
    #         zorder=10,
    #         # c=color,
    #         color="xkcd:dark",
    #         s=25,
    #     )

    if var in part_2:
        label, color = part_2[var]
        axes[i].scatter(
            daily_mean["datetime"],
            daily_mean[var],
            label=f"Measured {label}",
            # c=color,
            zorder=10,
            color="xkcd:dark",  # dark grey
            s=25,
        )

# Add fill_between for pH sensor uncertainty
        if var == "pH_insitu":
            axes[i].fill_between(  # Changed from axes.fill_between to axes[i].fill_between
                all_data["datetime"],
                all_data["pH_sensor"] - all_data["uncertainty"],  # Lower bound
                all_data["pH_sensor"] + all_data["uncertainty"],  # Upper bound
                color="xkcd:bubblegum pink",
                alpha=0.2,
                zorder=0
                # label="pH Sensor Uncertainty",
            )
    if var in part_3:
        continuous_var, continuous_color = part_3[var]
        axes[i].scatter(
            all_data["datetime"],
            all_data[continuous_var],
            label=f"Predicted {label}",
            # c=continuous_color,
            color="xkcd:sea blue",
            alpha=0.5,
            s=1,
            # edgecolor=None
        )
    
    if i ==5 or i ==6:
        axes[i].axhline(0, color='xkcd:black', alpha=0.8, ls='--')
    axes[i].set_ylabel(labels[i], fontsize=14)
    axes[i].tick_params(axis="y", labelsize=12)
    axes[i].grid(alpha=0.2)
    
    if i ==0 or i ==1:
        axes[i].set_ylabel(labels[i], labelpad=25)
        
    if i ==3:
        axes[i].set_ylabel(labels[i], labelpad=25)
        
    if i ==2 or i==4:
        axes[i].set_ylabel(labels[i], labelpad=15)
        
    if i ==5:
        axes[i].set_ylabel(labels[i], labelpad=30)
        
    if i ==6:
        axes[i].set_ylabel(labels[i], labelpad=25)       
            
ax_twin = axes[6].twinx()
ax_twin.plot(
    all_data["datetime"],
    all_data["cum_flux_test"],  
    c="xkcd:carnation",
    label="Cum.Flux",
    lw=3
)
ax_twin.set_ylim(-9, 10)
ax_twin.set_ylabel("Cumulative Flux / g-C m⁻²", fontsize=14, labelpad=10)
ax_twin.tick_params(axis="y", labelsize=12)
ax_twin.legend(frameon=False)

axes[0].tick_params(axis="x", labeltop=True)
axes[0].xaxis.set_ticks_position('top')

for i in range(6):
    axes[i].tick_params(axis='x', bottom=False)
    
for i, var in enumerate(params):
    axes[i].text(0.99, 0.05,
    f'({letters[i]})',
    transform=axes[i].transAxes,  
    fontsize=16,  
    fontweight='bold',
    ha='right',  
    va='bottom'    
    )
    
    
axes[-1].xaxis.set_major_locator(mdates.MonthLocator())  # One tick per month
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

plt.tight_layout()

