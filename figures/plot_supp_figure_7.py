import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# This script plots and calculates the temperal variability in the TA-DIC ratio.


# Import data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")


complete_data = all_data.dropna(subset=['predicted_alk_sal', 'calculated_dic'])


# Feb 2022 through Jan 2023
month_order = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]  # Feb=2, Mar=3, ..., Dec=12, Jan=1
month_names = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']

# Calculate monthly slopes
monthly_results = []
for i, month in enumerate(month_order):
    month_data = complete_data[complete_data['datetime'].dt.month == month]
    
    if len(month_data) > 10:  # Need enough points for meaningful regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            month_data['calculated_dic'], 
            month_data['predicted_alk_sal']
        )
        
        monthly_results.append({
            'month': month,
            'month_name': month_names[i],
            'chronological_order': i + 1,  # For plotting in correct order
            'slope': slope,
            'slope_error': std_err,
            'r_squared': r_value**2,
            'p_value': p_value,
            'n_points': len(month_data)
        })
    else:
        print(f"Not enough data for {month_names[i]}: {len(month_data)} points")

# Convert to DataFrame
monthly_df = pd.DataFrame(monthly_results)


# Plot monthly ratios in chronological order

fig, ax = plt.subplots(figsize=(6,3), dpi=600)
ax.plot(monthly_df['chronological_order'], monthly_df['slope'],c="xkcd:sea blue",lw=1.3,
        marker ="o", markersize=3.5)
plt.ylabel('ΔTA/ΔDIC', fontsize=9, labelpad=5)
plt.xlabel('',fontsize=9, labelpad=5)
plt.xticks(range(1, len(month_names) + 1), month_names)
plt.grid(alpha=0.25)
plt.axhline(y=0, c='xkcd:black', lw=0.8, linestyle='--', alpha=0.5)
ax.tick_params(axis="both", labelsize=6.5)
plt.tight_layout()




