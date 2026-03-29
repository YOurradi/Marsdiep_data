import pandas as pd
import matplotlib.pyplot as plt

# This script calculates and plots the yearly variability in temperature, 
# salinity, and NAO index between 2001-2023.


# import data
full_data = pd.read_parquet("Marsdiep_data/data/jetty_2001_2025.parquet")

# Selecting the period

full_data_copy = full_data.copy()

start_date = '2001-01-01'
end_date = '2024-12-31'
L = (full_data_copy['datetime'] >= start_date) & (full_data_copy['datetime'] <= end_date)
full_data_copy = full_data_copy[L].set_index('datetime')

# Make yearly mean for temp and sal
yearly_temperature = full_data_copy['temperature'].resample('Y').mean()
yearly_salinity = full_data_copy['salinity'].resample('Y').mean()


full_data_copy = full_data_copy.reset_index()
full_data_copy['year'] = full_data_copy['datetime'].dt.year

#Yearly average of temperature and slainity
yearly_avg_temp = full_data_copy.groupby('year')['temperature'].mean()
yearly_avg_sal = full_data_copy.groupby('year')['salinity'].mean()


# Import NAO index data
nao_index = pd.read_csv("jetty_processing/data/jetty_2001/nao_index.txt", sep='\s+', index_col=0)

nao_index.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
nao_index = nao_index.reset_index().rename(columns={'index': 'year'})
nao_index_long = nao_index.melt(id_vars=['year'], var_name='Month', value_name='index')

nao_yearly_mean = nao_index_long.groupby('year')['index'].mean().reset_index()
nao_yearly_mean.columns = ['year', 'nao_yearly_mean']

#Plotting
# Create figure and axes
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(17, 10), dpi=600, sharex=True)

# Twin axes for NAO index
ax1_nao = ax1.twinx()
ax2_nao = ax2.twinx()

# Bar width for NAO index
bar_width = 0.08

# Plot NAO index for temperature subplot
months = nao_index_long['Month'].unique()
for i, month in enumerate(months):
    month_data = nao_index_long[nao_index_long['Month'] == month]
    bar_colors = ['xkcd:red' if value >= 0 else 'xkcd:blue' for value in month_data['index']]
    ax1_nao.bar(month_data['year'] + i * bar_width, month_data['index'], width=bar_width, color=bar_colors, alpha=0.3)

# Plot yearly mean NAO index
ax1_nao.plot(nao_yearly_mean['year'], nao_yearly_mean['nao_yearly_mean'], color='xkcd:dark', linewidth=4, label="Yearly mean NAO")

# Plot yearly mean temperature
ax1.plot(yearly_avg_temp.index, yearly_avg_temp, color='xkcd:red', linewidth=4, label="Yearly mean temperature")

# Highlight the period from February 2022 to January 2023
highlight_start = 2022 + 1/12  # February 2022
highlight_end = 2023  # January 2023
ax1.axvspan(highlight_start, highlight_end, color='grey', alpha=0.3)

# Set labels and limits for temperature subplot
ax1.set_ylabel('Temperature / °C', fontsize=20, labelpad=30)
ax1_nao.set_ylabel('NAO Index', fontsize=20, labelpad=30)
ax1.set_ylim(9, 15)
ax1_nao.set_ylim(-4, 4)
ax1_nao.set_yticks([-4, -2, 0, 2, 4])  
ax1.set_xlim(2000, 2024)
ax1.grid(True, linestyle='-', alpha=0.25)
ax1.tick_params(axis="both", which="major", labelsize=18)
ax1_nao.tick_params(axis="y", labelsize=20)

# Add legend for temperature subplot
ax1.legend(fontsize=15, framealpha=0)
ax1_nao.legend( fontsize=15, framealpha=0)

# Plot NAO index for salinity subplot
for i, month in enumerate(months):
    month_data = nao_index_long[nao_index_long['Month'] == month]
    bar_colors = ['xkcd:red' if value >= 0 else 'xkcd:blue' for value in month_data['index']]
    ax2_nao.bar(month_data['year'] + i * bar_width, month_data['index'], width=bar_width, color=bar_colors, alpha=0.3)

# Plot yearly mean NAO index
ax2_nao.plot(nao_yearly_mean['year'], nao_yearly_mean['nao_yearly_mean'], color='xkcd:dark', linewidth=4, label="Yearly mean NAO")

# Plot yearly mean salinity
ax2.plot(yearly_avg_sal.index, yearly_avg_sal, color='xkcd:green', linewidth=4, label="Yearly mean salinity")

# Highlight the period from February 2022 to January 2023
ax2.axvspan(highlight_start, highlight_end, color='grey', alpha=0.3)

# Set labels and limits for salinity subplot
ax2.set_ylabel('Salinity', fontsize=20, labelpad=30)
ax2_nao.set_ylabel('NAO Index', fontsize=20, labelpad=30)
ax2.set_ylim(20, 35)  # Adjust salinity limits as needed
ax2_nao.set_ylim(-4, 4)
ax2_nao.set_yticks([-4, -2, 0, 2, 4])  # Add this line
ax2.grid(True, linestyle='-', alpha=0.25)
ax2.tick_params(axis="both", which="major", labelsize=18)
ax2_nao.tick_params(axis="y", labelsize=18)

# Add legend for salinity subplot
ax2.legend( fontsize=15, framealpha=0)
ax2_nao.legend(fontsize=15, framealpha=0)

# Set x-axis ticks and labels
year_ticks = range(2001, 2025, 2)
ax2.set_xticks(year_ticks)

# Adjust layout
plt.tight_layout()


