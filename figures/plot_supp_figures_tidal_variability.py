import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm


# This script plots the tidal variability for all variables across the months.

# Load data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

# Variables to analyze
variables = [
    "pH_sensor", "calculated_dic", "predicted_alk_sal",
    "temperature", "salinity", "water_level",
    "delta_interp1d"
]

# Month names in chronological order (Feb 2022 - Jan 2023)
month_names = [
    "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December", "January"
]

# Month order mapping for plotting (Feb=2, Mar=3, ..., Dec=12, Jan=1)
month_order = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]

# Y-axis labels
y_axis = {
    "pH_sensor": "pH",
    "calculated_dic": "DIC / μmol.kg⁻¹",
    "predicted_alk_sal": "TA / μmol.kg⁻¹",
    "temperature": "Temperature / °C",
    "salinity": "Salinity",
    "water_level": "Water Level / cm",
    "delta_interp1d": "∆fCO₂ / μatm",
}

# Calculate tidal phase 
tidal_period = 24/(12 + (25/60))  
all_data["tidal_datenum"] = (all_data["datenum"]) * tidal_period
all_data["tidal_datenum_mod"] = ((all_data["datenum"]) * tidal_period) % 1

# Create tidal phase bins
bin_edges = [i/10 for i in range(11)]  
all_data['tidal_phase_bin'] = pd.cut(all_data['tidal_datenum_mod'], bins=bin_edges)


for var in variables:
    fig, axes = plt.subplots(3, 4, figsize=(15, 10), dpi=300, sharey=True, sharex=True, constrained_layout=True)
    axes = axes.flatten()  
    
    for plot_idx, month in enumerate(month_order): 
        ax = axes[plot_idx]  
        month_data = all_data[all_data["datetime"].dt.month == month].copy()
        
        # Group by date and tidal phase
        daily_mean = month_data.groupby(
            [month_data["datetime"].dt.date, "tidal_phase_bin"]
        )[var].mean().reset_index()
        
        # Apply daily normalization (subtract daily mean)
        normalized_daily = daily_mean.copy()
        normalized_daily[var] = normalized_daily.groupby("datetime")[var].transform(lambda x: x - x.mean())
        
        # Apply monthly normalization (subtract monthly mean)
        monthly_mean_value = normalized_daily[var].mean()
        normalized_daily[var] = normalized_daily[var] - monthly_mean_value
        
        # Get unique dates for colormap
        unique_dates = normalized_daily["datetime"].unique()
        norm = mcolors.Normalize(vmin=0, vmax=len(unique_dates) - 1)
        cmap = cm.get_cmap("turbo")
        
        # Plot individual daily normalized data with turbo colormap
        for i, date in enumerate(unique_dates):
            day_data = normalized_daily[normalized_daily["datetime"] == date]
            bin_centers = [
                (interval.left + interval.right) / 2 for interval in day_data["tidal_phase_bin"]
            ]
            color = cmap(norm(i))
            ax.plot(bin_centers, day_data[var], alpha=0.6, color=color, label=f"Day {date}")
        
        # Calculate and plot monthly mean (normalized)
        monthly_mean = normalized_daily.groupby("tidal_phase_bin")[var].mean().reset_index()
        bin_centers_monthly = [
            (interval.left + interval.right) / 2 for interval in monthly_mean["tidal_phase_bin"]
        ]
        ax.plot(bin_centers_monthly, monthly_mean[var], color="black", linewidth=3.5, label="Monthly Mean")
        
        # Formatting (NO y-axis labels here)
        ax.set_xticks([0.2, 0.4, 0.6, 0.8])
        ax.tick_params(axis='both', labelsize=15)        
        ax.set_title(f"{month_names[plot_idx]}", fontsize=20, fontweight='bold')
        ax.grid(alpha=0.25)
    
    # Add single y-axis label for the entire figure (centered vertically)
    if var in y_axis:
        fig.text(-0.022, 0.5, y_axis[var], ha='center', va='center', rotation=90, fontsize=20)
    
    # Add single centered x-axis label for the entire figure
    fig.text(0.5, -0.028, 'Tidal phase', ha='center', va='bottom', fontsize=20)
    
    # Add a colorbar for the Turbo colormap
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=30))  # Assum
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, shrink=0.8, aspect=30, pad=0.02)
    cbar.set_label('Day', fontsize=20, rotation=360, labelpad=35)
    cbar.ax.tick_params(labelsize=15)
    

