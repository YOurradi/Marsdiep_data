import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.cm import get_cmap

# This script plots the seasonal diurnal variability for each variable.
#supplementary figures:8,9,11,14,17,19,21


# File paths
daily_path = "Marsdiep_data/data/daily_normalised_data/"
monthly_path = "Marsdiep_data/data/monthly_normalised_data/"

# Variables to plot
variables = [
    "pH_sensor", "calculated_dic", "predicted_alk_sal",
    "temperature", "salinity", "water_level",
    "delta_interp1d", "F_Ni00"
]

# Load monthly and daily means into dicts
monthly_means_dict = {
    var: pd.read_parquet(f"{monthly_path}{var}_normalised_monthly_hourly_means.parquet")
    for var in variables
}

daily_means_dict = {
    var: pd.read_parquet(f"{daily_path}{var}_normalised_daily_hourly_means.parquet")
    for var in variables
}

# Month names starting from February 2022 to January 2023
month_names = [
    "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December", "January"
]

# Y-axis labels
y_axis = {
    "pH_sensor": "pH",
    "calculated_dic": "DIC / μmol.kg⁻¹",
    "predicted_alk_sal": "TA / μmol.kg⁻¹",
    "temperature": "Temperature / °C",
    "salinity": "Salinity",
    "water_level": "Water Level / cm",
    "delta_interp1d": "ΔfCO₂ / μatm",
    "F_Ni00": "FCO₂ / g-C m⁻² d⁻¹",
}

# Turbo colormap
turbo_cmap = get_cmap("turbo")


for var in variables:
    fig, axes = plt.subplots(3, 4, figsize=(14, 9), dpi=300, sharey=True, sharex=True, constrained_layout=True)
    monthly_cycle = monthly_means_dict[var]
    daily_cycle = daily_means_dict[var]
    # Iterate over months in the correct order (February 2022 to January 2023)
    for month_idx, ax in zip(range(2, 14), axes.flatten()):  
        month = month_idx if month_idx <= 12 else month_idx - 12  
        # Filter daily data for the current month
        daily_cycle.index = pd.to_datetime(daily_cycle.index)
        month_daily_data = daily_cycle[daily_cycle.index.month == month]
        # Get the number of days in the month for color mapping
        num_days = len(month_daily_data)
        colors = turbo_cmap(np.linspace(0, 1, num_days))  # Generate colors for each day
        # Plot daily cycles with Turbo colormap
        for (day, day_data), color in zip(month_daily_data.iterrows(), colors):
            ax.plot(
                day_data.index,
                day_data.values,
                color=color,  # Use Turbo colormap colors
                alpha=0.7,  # Adjust transparency
                linewidth=1.5,
            )
        # Plot monthly mean
        if month in monthly_cycle.index:
            ax.plot(
                monthly_cycle.columns,
                monthly_cycle.loc[month],
                label="Monthly Mean",
                c="black",
                linewidth=3.5,
            )
        # Add horizontal line at y=0
        ax.axhline(0, color="xkcd:black", linestyle="-", linewidth=1.5, alpha=0.8)
        # Make it pretty
        ax.set_xticks(range(0, 24, 4))
        ax.set_title(month_names[month_idx - 2], fontsize=18, fontweight="bold")  # Adjust index for month_names
        ax.set_xlim(0, 23)
        ax.tick_params(axis='both', labelsize=16)
        ax.grid(alpha=0.25)
    
    # Add single y-axis label for the entire figure (centered vertically)
    if var in y_axis:
        fig.text(-0.020, 0.5, y_axis[var], ha='center', va='center', rotation=90, fontsize=20)
    
    # Add single centered x-axis label for the entire figure
    fig.text(0.5, -0.028, 'Hour of Day', ha='center', va='bottom', fontsize=20)
    
    # Add a colorbar for the Turbo colormap
    sm = plt.cm.ScalarMappable(cmap=turbo_cmap, norm=plt.Normalize(vmin=1, vmax=31))  # Days of the month
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, shrink=0.8, aspect=30, pad=0.02)
    cbar.set_label('Day', fontsize=20, rotation=360, labelpad=35)
    cbar.ax.tick_params(labelsize=15)
    

plt.close()