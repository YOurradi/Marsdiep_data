import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# This script plots the monrthly and daily anomlaies of the different variables
# across tidal phases

# Load data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

# Variables to analyze 
variables = [
    "predicted_alk_sal",  
    "temperature", 
    "salinity", 
    "calculated_dic",     
    "pH_sensor"          
]

# Selected months only (March, June, September, December)
selected_months = [3, 6, 9, 12]
month_names = ["March", "June", "September", "December"]

# Y-axis labels
y_axis = {
    "calculated_dic": "DIC / μmol.kg⁻¹",
    "predicted_alk_sal": "TA / μmol.kg⁻¹",
    "temperature": "Temperature / °C",
    "salinity": "Salinity",
    "pH_sensor": "pH",
}

# Calculate tidal phase 
tidal_period = 24/(12 + (25/60))  
all_data["tidal_datenum"] = (all_data["datenum"]) * tidal_period
all_data["tidal_datenum_mod"] = ((all_data["datenum"]) * tidal_period) % 1

# Create tidal phase bins
bin_edges = [i/10 for i in range(11)]  
all_data['tidal_phase_bin'] = pd.cut(all_data['tidal_datenum_mod'], bins=bin_edges)

variables = [
    "temperature", 
    "salinity",
    "predicted_alk_sal",   
    "calculated_dic",     
    "pH_sensor"           
]

season_month_names = {
    1: "Winter (January)",
    2: "Winter (February)",
    3: "Spring (March)",
    4: "Spring (April)", 
    5: "Spring (May)",
    6: "Summer (June)",
    7: "Summer (July)",
    8: "Summer (August)",
    9: "Autumn (September)",
    10: "Autumn (October)",
    11: "Autumn (November)",
    12: "Winter (December)"
}


# Variables to analyze (selected 5)
variables = [
    "predicted_alk_sal",  # TA
    "temperature", 
    "salinity", 
    "calculated_dic",     # DIC
    "pH_sensor"           # pH
]

# Selected months only (March, June, September, December)
selected_months = [3, 6, 9, 12]
month_names = ["March", "June", "September", "December"]

# Y-axis labels
y_axis = {
    "calculated_dic": "DIC / μmol.kg⁻¹",
    "predicted_alk_sal": "TA / μmol.kg⁻¹",
    "temperature": "Temperature / °C",
    "salinity": "Salinity",
    "pH_sensor": "pH",
}

# Calculate tidal phase (your existing method)
tidal_period = 24/(12 + (25/60))  
all_data["tidal_datenum"] = (all_data["datenum"]) * tidal_period
all_data["tidal_datenum_mod"] = ((all_data["datenum"]) * tidal_period) % 1

# Create tidal phase bins
bin_edges = [i/10 for i in range(11)]  
all_data['tidal_phase_bin'] = pd.cut(all_data['tidal_datenum_mod'], bins=bin_edges)

variables = [
    "temperature", 
    "salinity",
    "predicted_alk_sal",   
    "calculated_dic",     
    "pH_sensor"           
]

season_month_names = {
    1: "Winter (January)",
    2: "Winter (February)",
    3: "Spring (March)",
    4: "Spring (April)", 
    5: "Spring (May)",
    6: "Summer (June)",
    7: "Summer (July)",
    8: "Summer (August)",
    9: "Autumn (September)",
    10: "Autumn (October)",
    11: "Autumn (November)",
    12: "Winter (December)"
}

fig, axes = plt.subplots(5, 4, figsize=(14, 14), dpi=300, sharey='row', sharex=True, constrained_layout=True)

# Loop through each variable (rows)
for var_idx, var in enumerate(variables):
    # Loop through each month (columns)
    for month_idx, month in enumerate(selected_months):
        ax = axes[var_idx, month_idx]
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
            ax.plot(bin_centers, day_data[var], alpha=0.6, color=color, linewidth=1)
        
        # Calculate and plot monthly mean (normalized)
        monthly_mean = normalized_daily.groupby("tidal_phase_bin")[var].mean().reset_index()
        bin_centers_monthly = [
            (interval.left + interval.right) / 2 for interval in monthly_mean["tidal_phase_bin"]
        ]
        ax.plot(bin_centers_monthly, monthly_mean[var], color="black", linewidth=3.5, label="Monthly Mean")
        
        #  Add HT and LT text labels ONLY to the last row**
        if var_idx == len(variables) - 1:  # Last row (pH_sensor)
            # Get y-axis limits to position text at the top
            # y_min, y_max = ax.get_ylim()
            y_text = -0.06
            
            # Add text labels
            ax.text(0.13, y_text, 'HT', fontsize=12, fontweight='bold', 
                   ha='center', va='top', color='xkcd:dark')
            ax.text(0.5, y_text, 'LT', fontsize=12, fontweight='bold', 
                   ha='center', va='top', color='xkcd:dark')
            ax.text(0.89, y_text, 'HT', fontsize=12, fontweight='bold', 
                   ha='center', va='top', color='xkcd:dark')
        
        # Y-axis labels only for first column
        if month_idx == 0:  # First column
            fig.text(-0.3, 0.5, y_axis[var], transform=ax.transAxes, fontsize=15, ha='center', va='center', rotation=90)
        
        # Column titles only for top row
        if var_idx == 0:  # Top row (first variable)
            ax.set_title(f"{season_month_names[month]}", fontsize=15, fontweight='bold')
        
        ax.tick_params(axis='both', labelsize=14)
        ax.grid(alpha=0.25)
        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_xticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1.0'])

# Add colorbar
# Create a ScalarMappable for the colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=30))  # Assuming max ~30 days
sm.set_array([])

# Add colorbar to the right of the entire plot
cbar = fig.colorbar(sm, ax=axes, shrink=0.8, aspect=30, pad=0.02)
cbar.set_label('Day', fontsize=15, rotation=360, labelpad=35)
cbar.ax.tick_params(labelsize=14)

# Add single centered x-axis label for the entire figure
fig.text(0.5, -0.028, 'Tidal phase', ha='center', va='bottom', fontsize=15)

