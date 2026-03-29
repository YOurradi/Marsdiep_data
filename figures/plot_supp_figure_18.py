import matplotlib.pyplot as plt
import pandas as pd
import PyCO2SYS as pyco2

# This script recalculates the effect of temperature variability on pH

# Import data
data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")


# Define months and days to plot
months = [3, 6, 9, 12]  # March, June, September, December
month_names = ['March', 'June', 'September', 'December']
days = [15,16,17, 18]  # Days 13-16
year = 2022

# Create subplots: 4 rows (months), 4 columns (days)
fig, axes = plt.subplots(4, 4,dpi=600, figsize=(20, 16), sharex=True, sharey=True)

# Calculate monthly means for carbonate chemistry for each month
monthly_means = {}
for month in months:
    month_data = data[(data['datetime'].dt.year == year) & 
                     (data['datetime'].dt.month == month)].copy()
    if len(month_data) > 0:
        monthly_means[month] = {
            'ta': month_data['predicted_alk_sal'].mean(),
            'dic': month_data['calculated_dic'].mean(),
            'sal': month_data['salinity'].mean()
        }
        print(f"{month_names[months.index(month)]} means - TA: {monthly_means[month]['ta']:.1f}, "
              f"DIC: {monthly_means[month]['dic']:.1f}, Salinity: {monthly_means[month]['sal']:.1f}")

# First pass: collect all pH values to determine global y-axis limits
all_measured_pH = []
all_temp_only_pH = []

for month in months:
    month_data = data[(data['datetime'].dt.year == year) & 
                     (data['datetime'].dt.month == month)].copy()
    
    if month not in monthly_means:
        continue
        
    for day in days:
        target_date = pd.to_datetime(f'{year}-{month:02d}-{day:02d}')
        day_data = month_data[month_data['datetime'].dt.date == target_date.date()].copy()
        
        if len(day_data) > 0:
            day_data['hour'] = day_data['datetime'].dt.hour
            hourly_means = day_data.groupby('hour').agg({
                'temperature': 'mean',
                'pH_sensor': 'mean'
            }).reset_index()
            
            hourly_means = hourly_means.dropna(subset=['pH_sensor'])
            
            if len(hourly_means) >= 6:  # At least 6 hours of data
                try:
                    results = pyco2.sys(
                        par1=monthly_means[month]['ta'], 
                        par2=monthly_means[month]['dic'], 
                        par1_type=1, 
                        par2_type=2,
                        temperature=hourly_means['temperature'].values, 
                        salinity=monthly_means[month]['sal']
                    )
                    temp_only_pH = results["pH_total"]
                    
                    all_measured_pH.extend(hourly_means['pH_sensor'].values)
                    all_temp_only_pH.extend(temp_only_pH)
                except:
                    pass

# Calculate global y-axis limits
if all_measured_pH and all_temp_only_pH:
    y_min = min(min(all_measured_pH), min(all_temp_only_pH)) - 0.02
    y_max = max(max(all_measured_pH), max(all_temp_only_pH)) + 0.02
else:
    y_min, y_max = 7.8, 8.2  # Default range

def process_day(day_data, ax, month, day, monthly_means):
    """Process a single day of data"""
    
    # Calculate hourly means for this day
    day_data['hour'] = day_data['datetime'].dt.hour
    hourly_means = day_data.groupby('hour').agg({
        'temperature': 'mean',
        'pH_sensor': 'mean'
    }).reset_index()
    
    # Remove rows with NaN pH_sensor values
    hourly_means = hourly_means.dropna(subset=['pH_sensor'])
    
    # Skip if not enough data
    if len(hourly_means) < 6:
        ax.text(0.5, 0.5, f'{month_names[months.index(month)]} {day}\nNo data', 
                transform=ax.transAxes, ha='center', va='center', fontsize=8)
        ax.set_xlim(0, 23)
        ax.grid(True, alpha=0.3)
        # Set larger tick sizes
        ax.tick_params(axis='x', labelsize=14)
        ax.tick_params(axis='y', labelsize=14)
        return
    
    # Plot the measured pH daily cycle first
    ax.plot(hourly_means['hour'], hourly_means['pH_sensor'], 
            c='xkcd:sea blue', linewidth=4.5,
            label='pH$_{meas}$')
    
    try:
        # Calculate temperature-only pH using monthly mean TA, DIC, sal
        results = pyco2.sys(
            par1=monthly_means[month]['ta'], 
            par2=monthly_means[month]['dic'], 
            par1_type=1, 
            par2_type=2,
            temperature=hourly_means['temperature'].values,
            salinity=monthly_means[month]['sal']
        )
        temp_only_pH = results["pH_total"]
        
        # Plot the temperature-only pH daily cycle
        ax.plot(hourly_means['hour'], temp_only_pH, 
                c="xkcd:raspberry", linewidth=4.5,  markersize=4, 
                 label='pH$_{temp}$')
                
    except Exception as e:
        print(f"Calculation error for {month_names[months.index(month)]} {day}: {e}")
        # Still plot measured pH even if calculation fails
        pass
    
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 23)
    ax.set_xticks([0, 6, 12, 18, 23])
    
    # Set larger tick sizes
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)
    
    # Set consistent y-axis limits for all subplots
    ax.set_ylim(y_min, y_max)

# Process each month and day combination
for month_idx, month in enumerate(months):
    month_data = data[(data['datetime'].dt.year == year) & 
                     (data['datetime'].dt.month == month)].copy()
    
    if month not in monthly_means:
        # Fill row with "No data" if month has no data
        for day_idx, day in enumerate(days):
            ax = axes[month_idx, day_idx]
            ax.text(0.5, 0.5, f'{month_names[month_idx]} {day}\nNo data', 
                    transform=ax.transAxes, ha='center', va='center', fontsize=8)
            ax.set_xlim(0, 23)
            ax.set_ylim(y_min, y_max)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', labelsize=14)
            ax.tick_params(axis='y', labelsize=14)
        continue
    
    for day_idx, day in enumerate(days):
        ax = axes[month_idx, day_idx]
        
        # Filter data for this specific day
        target_date = pd.to_datetime(f'{year}-{month:02d}-{day:02d}')
        day_data = month_data[month_data['datetime'].dt.date == target_date.date()].copy()
        
        if len(day_data) > 0:
            process_day(day_data, ax, month, day, monthly_means)
        else:
            ax.text(0.5, 0.5, f'{month_names[month_idx]} {day}\nNo data', 
                    transform=ax.transAxes, ha='center', va='center', fontsize=8)
            ax.set_xlim(0, 23)
            ax.set_ylim(y_min, y_max)
            ax.grid(True, alpha=0.25)
            ax.tick_params(axis='x', labelsize=16)
            ax.tick_params(axis='y', labelsize=16)

# Add column headers (days)
for day_idx, day in enumerate(days):
    axes[0, day_idx].set_title(f'Day {day}', fontsize=20, fontweight='bold')

# Add row labels (months) - larger font size for month names
for month_idx, month_name in enumerate(month_names):
    axes[month_idx, 0].set_ylabel(f'{month_name}', fontsize=20, rotation=360, labelpad=70)

# Add legend using the first subplot that has data
legend_added = False
for month_idx in range(4):
    for day_idx in range(4):
        ax = axes[month_idx, day_idx]
        if ax.get_legend_handles_labels()[0]:  # If there are legend items
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper right', fontsize=24,frameon=False, fancybox=False, bbox_to_anchor=(0.95, 0.16))
            legend_added = True
            break
    if legend_added:
        break

# Add a single x-axis title for the entire figure
fig.text(0.5, 0.02, 'Hour of Day', ha='center', fontsize=26)

# Add a single y-axis title for the entire figure  
fig.text(0.02, 0.5, 'pH', va='center', rotation='vertical', fontsize=26)

plt.tight_layout()
plt.subplots_adjust(left=0.10, right=0.95, top=0.95, bottom=0.08)
