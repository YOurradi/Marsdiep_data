import pandas as pd, numpy as np
import function
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


# This script plots the semivariogram plot using absolute pH offset differences.

# Import data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

file_path = "Marsdiep_data/data/all_jetty_results.parquet"

# Applying kriging functions from script: function

datenum_values, offset_values, diff_offset, diff_datenum, all_data = function.get_data(file_path)

bin_edges = function.get_bin_edges()

(
    bin_datenum_means,
    bin_offset_means,
    bin_offset_sigma,
    bin_indices,
    bin_count,
) = function.get_semivariogram(diff_datenum, diff_offset, bin_edges)


bins = np.arange(0, 351, 5)

def uncertainty(datenum, a, b, c):

    return a * np.sqrt(datenum) + b + c * datenum

# remove the nan values
bin_datenum_means = np.array(bin_datenum_means)
bin_offset_sigma = np.array(bin_offset_sigma)

L = ~np.isnan(bin_datenum_means) & ~np.isnan(bin_offset_sigma)

bin_datenum_means = bin_datenum_means[L]
bin_offset_sigma = bin_offset_sigma[L]

L2 = bin_datenum_means < 60

optimum, covariance = curve_fit(
    uncertainty, bin_datenum_means[L2], bin_offset_sigma[L2]
)
best_fit = uncertainty(bin_datenum_means, *optimum)

# Use function again to calculate uncertainty

all_data = function.calculate_uncertainty(all_data, optimum)


fig, ax2 = plt.subplots(figsize= (6,3), dpi=300)
ax2.scatter(
    bin_datenum_means,
    bin_offset_sigma,
    c="xkcd:sea blue",
    s=4.5,
)
ax2.scatter(
    diff_datenum,
    np.abs(diff_offset),
    marker="o", 
    c="xkcd:bluegrey",
    alpha=0.2,
    s=3
)
ax2.plot(
    bin_datenum_means,
    best_fit,
    c="red",
    lw=1,
)
ax2.set_xlim(0, 100)
ax2.set_ylim(0, 0.37)
ax2.set_xlabel("Time difference (day)", fontsize=8, labelpad=3)
ax2.set_ylabel("Absolute offset difference", fontsize=8, labelpad=3)
ax2.grid(alpha=0.3, ls="-")
ax2.tick_params(axis="both", labelsize=6.5)

for spine in ax2.spines.values():
    spine.set_color('black')        
    spine.set_linewidth(0.4) 
    
ax2.tick_params(
    axis='both',       
    which='both',      
    direction='out',   
    length=1.5,          
    width=0.4,         
    colors='black'      
)
    
plt.tight_layout()
