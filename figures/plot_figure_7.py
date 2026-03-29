import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.cm import get_cmap

# THis script plots the monthly and daily anomalies of the different variables

# File paths
daily_path = "Marsdiep_data/data/daily_normalised_data/"
monthly_path = "Marsdiep_data/data/monthly_normalised_data/"

# Variables to plot
variables = [
    "temperature", "salinity", "predicted_alk_sal", "calculated_dic", "pH_sensor", "delta_interp1d"
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

# Y-axis labels
y_axis = {
    "temperature": "Temperature / °C",
    "salinity": "Salinity",
    "predicted_alk_sal": "TA / μmol.kg⁻¹",
    "calculated_dic": "DIC / μmol.kg⁻¹",
    "pH_sensor": "pH",
    "delta_interp1d": "ΔfCO₂ / μatm"
}

# Turbo colormap
turbo_cmap = get_cmap("turbo")

# Selected months for each season (using month names)
season_months = {
    "Spring": "March",
    "Summer": "June",
    "Fall": "September",
    "Winter": "December"

}

# Map month names to month numbers
month_name_to_number = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

# Calculate y-axis limits for each variable (across all seasons)
y_limits = {}
for var in variables:
    all_values = []
    
    # Collect all values from daily data for each season
    for season, month_name in season_months.items():
        month = month_name_to_number[month_name]
        daily_cycle = daily_means_dict[var]
        daily_cycle.index = pd.to_datetime(daily_cycle.index)
        month_daily_data = daily_cycle[daily_cycle.index.month == month]
        all_values.extend(month_daily_data.values.flatten())
    
    # Also include monthly means
    monthly_cycle = monthly_means_dict[var]
    for season, month_name in season_months.items():
        month = month_name_to_number[month_name]
        if month in monthly_cycle.index:
            all_values.extend(monthly_cycle.loc[month].values)
    
    # Calculate limits with some padding
    y_min, y_max = np.nanmin(all_values), np.nanmax(all_values)
    y_range = y_max - y_min
    padding = y_range * 0.05  # 5% padding
    y_limits[var] = (y_min - padding, y_max + padding)


# Plotting
fig, axes = plt.subplots(6, 4, figsize=(12.5, 12.5), dpi=300, sharex=True, constrained_layout=True)

for i, var in enumerate(variables):
    for j, (season, month_name) in enumerate(season_months.items()):
        ax = axes[i, j]

        # Get the month number from the month name
        month = month_name_to_number[month_name]

        # Get monthly and daily data for the selected month
        monthly_cycle = monthly_means_dict[var]
        daily_cycle = daily_means_dict[var]

        # Filter daily data for the current month
        daily_cycle.index = pd.to_datetime(daily_cycle.index)
        month_daily_data = daily_cycle[daily_cycle.index.month == month]

        # Get the number of days in the month for color mapping
        num_days = len(month_daily_data)
        
        # Create color mapping based on day of month
        day_numbers = [day.day for day in month_daily_data.index]
        colors = turbo_cmap(np.array(day_numbers) / 31)  # Normalize to 0-1 based on max days in month

        # Plot daily cycles with Turbo colormap
        for (day, day_data), color in zip(month_daily_data.iterrows(), colors):
            ax.plot(
                day_data.index,
                day_data.values,
                color=color,  
                alpha=0.7, 
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

        # Set consistent y-axis limits for this variable across all seasons
        ax.set_ylim(y_limits[var])

        # Make it pretty
        ax.set_xticks(range(0, 24, 4))
        # if j == 0:  # Add y-axis labels only for the first column
        #     ax.set_ylabel(y_axis[var], fontsize=24, labelpad=60)
        
        if j == 0:  # Add y-axis labels only for the first column
            fig.text(-0.3, 0.5,y_axis[var],   transform=ax.transAxes,
              fontsize=17, ha='center', va='center', rotation=90)

        # Set title for the first row only
        if i == 0:
            ax.set_title(f"{season} ({month_name})", fontsize=15, fontweight="bold")

        # Only show y-axis ticks and labels for the first column
        if j == 0:
            ax.tick_params(axis='both', labelsize=14)
        else:
            ax.tick_params(axis='x', labelsize=14)  # Only x-axis ticks for other columns
            ax.tick_params(axis='y', left=False, labelleft=False)  # Hide y-axis ticks and labels
        ax.grid(alpha=0.25)

# Add a colorbar for the Turbo colormap
sm = plt.cm.ScalarMappable(cmap=turbo_cmap, norm=plt.Normalize(vmin=1, vmax=31))  # Days of the month
sm.set_array([])
cbar = fig.colorbar(sm, ax=axes, shrink=0.6, aspect=30, pad=0.02)
cbar.set_label('Day', fontsize=20,rotation=360, labelpad=25)
cbar.ax.tick_params(labelsize=15)


fig.text(0.5,-0.02, 'Hour of Day', ha='center', va='bottom', fontsize=17)

