import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# This script plots the model performance evaluation of the TA prediction model.

# Import data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

# Residuals Alkalinity 
alkalinity_data = all_data.dropna(subset=['alkalinity', 'predicted_alk_sal']).copy()
alkalinity_data['datetime'] = pd.to_datetime(alkalinity_data['datetime'])
alkalinity_data['residuals'] = alkalinity_data['alkalinity'] - alkalinity_data['predicted_alk_sal']
alkalinity_data['month'] = alkalinity_data['datetime'].dt.month
alkalinity_data['month_name'] = alkalinity_data['datetime'].dt.strftime('%b')

# daily avg 
alkalinity_data['date'] = alkalinity_data['datetime'].dt.date
daily_residuals = alkalinity_data.groupby('date').agg({
    'alkalinity': 'mean',           
    'predicted_alk_sal': 'first',   # Keep 1st predicted alkalinity value
    'datetime': 'first'             # Keep 1st datetime of the day
}).reset_index()

# Residuals with daily avg
daily_residuals['residuals'] = daily_residuals['alkalinity'] - daily_residuals['predicted_alk_sal']
daily_residuals['month'] = daily_residuals['datetime'].dt.month
daily_residuals['month_name'] = daily_residuals['datetime'].dt.strftime('%b')

# Calculate RMSD and its standard error using bootstrap
def calculate_rmsd(measured, predicted):
    return np.sqrt(np.mean((measured - predicted)**2))

def calculate_rmsd_stderr(measured, predicted, n_bootstrap=1000):
    """
    Calculate RMSD standard error using bootstrap resampling
    """
    if len(measured) <= 1:
        return np.nan  # if n<= 1 , then can't calc RMSD
    
    n = len(measured)
    rmsd_bootstrap = []
    
    # Bootstrap resampling
    for _ in range(n_bootstrap):

        indices = np.random.choice(n, size=n, replace=True) # for random resampling
        boot_measured = measured.iloc[indices] 
        boot_predicted = predicted.iloc[indices] 
        
        #  RMSD for this bootstrap 
        boot_rmsd = calculate_rmsd(boot_measured, boot_predicted)
        rmsd_bootstrap.append(boot_rmsd)
    
    # std = std of the bootstrap of rmsd 
    return np.std(rmsd_bootstrap)

#  monthly statistics + std
monthly_stats = []
for month in range(1, 13):
    # Alkalinity stats from alkalinity dataset
    month_alkalinity = alkalinity_data[alkalinity_data['month'] == month]
    # Daily data 
    month_daily = daily_residuals[daily_residuals['month'] == month]
    
    if len(month_alkalinity) > 0:  # only months with alkalinity data
        rmsd = calculate_rmsd(month_alkalinity['alkalinity'], month_alkalinity['predicted_alk_sal'])
        rmsd_se = calculate_rmsd_stderr(month_alkalinity['alkalinity'], month_alkalinity['predicted_alk_sal'])
        n_alk_samples = len(month_alkalinity)
            
        monthly_stats.append({
            'month': month,
            'month_name': month_alkalinity['month_name'].iloc[0],
            'n_alkalinity_samples': n_alk_samples,      # nbr of alkalinity measurements
            'n_days': len(month_daily),                 # nbr of days with alkalinity data
            'RMSD': rmsd,
            'RMSD_SE': rmsd_se
        })

monthly_df = pd.DataFrame(monthly_stats)

# Calculate overall RMSD std 
overall_rmsd = calculate_rmsd(alkalinity_data['alkalinity'], alkalinity_data['predicted_alk_sal'])
overall_rmsd_se = calculate_rmsd_stderr(alkalinity_data['alkalinity'], alkalinity_data['predicted_alk_sal'])


# month order becasue feb 2022 and jan 2023
chronological_order = [ 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']

#  months with data, in chronological order
available_months = set(monthly_df['month_name'].unique())
plot_order = [m for m in chronological_order if m in available_months]

# order by month
month_order_dict = {month: i for i, month in enumerate(chronological_order)}
monthly_df['sort_order'] = monthly_df['month_name'].map(month_order_dict)
monthly_df = monthly_df.sort_values('sort_order').reset_index(drop=True)

# Plotting
fig, axes = plt.subplots(3, 1, figsize=(10, 12), dpi=600)

# subpplot 1: Predicted vs Measured 
ax1 = axes[0]
ax1.scatter(alkalinity_data['alkalinity'], alkalinity_data['predicted_alk_sal'], 
           s=30, alpha=0.8, c='xkcd:sea blue')

# Add 1:1 line
min_val = min(alkalinity_data['alkalinity'].min(), alkalinity_data['predicted_alk_sal'].min())
max_val = max(alkalinity_data['alkalinity'].max(), alkalinity_data['predicted_alk_sal'].max())
ax1.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, alpha=0.8)

ax1.set_xlabel('TA / µmol kg⁻¹', fontsize=12)
ax1.set_ylabel('TA$_{pred}$ / µmol kg⁻¹', fontsize=12)
ax1.set_title('Predicted vs Measured Alkalinity', fontsize=14, fontweight='bold')
ax1.tick_params(axis='x', labelsize=11)
ax1.tick_params(axis='y', labelsize=11)
ax1.grid(True, alpha=0.3)

# R2 and RMSD
r_value, _ = pearsonr(alkalinity_data['alkalinity'], alkalinity_data['predicted_alk_sal'])
r_squared = r_value**2

# Add statistics text box
stats_text = f'R² = {r_squared:.3f}\nRMSD = {overall_rmsd:.1f} µmol kg⁻¹\nn = {len(alkalinity_data)}'
ax1.text(0.015, 0.95, stats_text, transform=ax1.transAxes, fontsize=11,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='none', edgecolor='none'))

# subplot 2: Residuals vs time 
ax2 = axes[1]
scatter = ax2.scatter(daily_residuals['datetime'], daily_residuals['residuals'], 
                      s=30, c='xkcd:sea blue')
ax2.axhline(y=0, c='xkcd:black', linestyle=':', linewidth=2)
ax2.set_ylabel('TA Residuals / µmol kg⁻¹)', fontsize=12)
ax2.set_title('Alkalinity residual', fontsize=14, fontweight='bold')
ax2.tick_params(axis='x', rotation=45, labelsize=11)
ax2.tick_params(axis='y', labelsize=11)
ax2.grid(True, alpha=0.3)

# subplot3: Monthly model performance (RMSD) + error bars
ax3 = axes[2]
bars = ax3.bar(monthly_df['month_name'], monthly_df['RMSD'], 
               # yerr=monthly_df['RMSD_SE'], capsize=5,,  # Add error bars
               color='xkcd:sea blue', edgecolor='xkcd:dark blue', alpha=0.7, linewidth=1.5,
                error_kw={'linewidth': 1.5, 'capthick': 1.5})
ax3.axhline(y=overall_rmsd, c='xkcd:black', linestyle='--', linewidth=1.5, 
            label=f'RMSD ({overall_rmsd:.1f} µmol kg⁻¹)')
ax3.set_ylabel('RMSD / µmol kg⁻¹', fontsize=12)
ax3.set_title('Monthly Model Performance', fontsize=14, fontweight='bold')
ax3.legend(fontsize=11)
ax3.tick_params(axis='x', rotation=45, labelsize=11)
ax3.tick_params(axis='y', labelsize=11)
ax3.grid(True, alpha=0.3, axis='y')

# add n values inside alk bars
for bar, n in zip(bars, monthly_df['n_alkalinity_samples']):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height/2,
             f'n={n}', ha='center', va='center', fontsize=10, fontweight='bold', 
             color='black')


# Add subplot labels
ax1.text(0.99, 0.02, '(a)', transform=ax1.transAxes, 
         fontsize=14, fontweight='bold', va='bottom', ha='right')

ax2.text(0.99, 0.02, '(b)', transform=ax2.transAxes, 
         fontsize=14, fontweight='bold', va='bottom', ha='right')

ax3.text(0.99, 0.02, '(c)', transform=ax3.transAxes, 
         fontsize=14, fontweight='bold', va='bottom', ha='right')

plt.tight_layout(pad=3.0)

