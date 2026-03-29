import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft, fftfreq

# This script calculalte the Fourier analysis of the data for each month and plot it.

# Import data
data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")

columns = ["pH_sensor", "calculated_dic", "predicted_alk_sal", "water_level", "temperature", "salinity", "delta_interp1d", "F_Ni00"]
sample_rate = float(1 / 144)

# Filtering the NaN values
L = data[columns].notnull().all(axis=1)
data = data[L]

# Fourier analysis function
def fourier_analysis(data, columns, sample_rate):
    fft_results = {}
    for column in columns:
        if column in data.columns:
            signal = data[column].values
            assert not np.any(np.isnan(signal)), f"Column '{column}' contains NaN values."
            N = len(signal)
            fft_values = fft(signal)
            frequency = fftfreq(N, sample_rate)
            fft_results[column] = {
                "fft": fft_values,
                "frequency": frequency
            }
    return fft_results

# Applying the Fourier analysis for each month
monthly_results = {}
for month, group in data.groupby('month'):
    L = group[columns].notnull().all(axis=1)
    group = group[L]
    fft_months = fourier_analysis(group, columns, sample_rate)
    monthly_results[month] = fft_months

# Function to calculate the amplitude ratio
def calculate_amplitude_ratio(frequency, fft_values, freq1=1, freq2=2, margin=0.2):
    freq1_range = (frequency > (freq1 - margin)) & (frequency < (freq1 + margin))
    freq2_range = (frequency > (freq2 - margin)) & (frequency < (freq2 + margin))
    peak_freq1_amplitude = np.max(np.abs(fft_values[freq1_range]))
    peak_freq2_amplitude = np.max(np.abs(fft_values[freq2_range]))
    if peak_freq2_amplitude > 0:  # Avoid division by zero
        ratio = peak_freq1_amplitude / peak_freq2_amplitude
    else:
        ratio = np.nan
    return peak_freq1_amplitude, peak_freq2_amplitude, ratio

# Calculate ratios for each month and variable
ratios = {
    "calculated_dic": [],
    "pH_sensor": [],
    "predicted_alk_sal": [],
    "temperature": [],
    "salinity": [],
    "water_level": [],
    "delta_interp1d": [],
    "F_Ni00": []
}

columns = ["calculated_dic", "pH_sensor", "predicted_alk_sal", "temperature", "salinity",
           "water_level", "delta_interp1d", "F_Ni00"]

# Ensure months are processed in the correct order (February 2022 to January 2023)
month_order = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]  # February to January

for month in month_order:
    if month in monthly_results:
        results = monthly_results[month]
        for col in columns:
            if col in results:  # Ensure the column exists in results
                fft_values = results[col]["fft"]
                frequency = results[col]["frequency"]

                # Only keep positive frequencies
                L = frequency > 0
                frequency = frequency[L]
                fft_values = fft_values[L]

                # Calculate the ratio
                peak_freq1, peak_freq2, amplitude_ratio = calculate_amplitude_ratio(
                    frequency, fft_values, freq1=1, freq2=2, margin=0.2
                )
                ratios[col].append(amplitude_ratio)

# Access ratios for each column
ratios_pH = ratios["pH_sensor"]
ratios_dic = ratios["calculated_dic"]
ratios_ta = ratios["predicted_alk_sal"]
ratios_temp = ratios["temperature"]
ratios_sal = ratios["salinity"]
ratios_wl = ratios["water_level"]
ratios_delta = ratios["delta_interp1d"]
ratios_flux = ratios["F_Ni00"]


# Reorder months to start with February and end with January
months = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']

# Plotting
fig, ax = plt.subplots(figsize=(15, 8), dpi=600)
ax.plot(range(1, 13), ratios_dic, marker="o", lw=4, c="xkcd:wine red", label="DIC")
ax.plot(range(1, 13), ratios_pH, marker="o", lw=4, c="xkcd:royal purple", label="pH")
ax.plot(range(1, 13), ratios_ta, marker="o", lw=4, c="xkcd:sky", label="TA")
ax.plot(range(1, 13), ratios_temp, marker="o", lw=4, c="xkcd:cobalt blue", label="Temperature")
ax.plot(range(1, 13), ratios_sal, marker="o", lw=4, c="xkcd:electric blue", label="Salinity")

ax.axhline(y=1, c='xkcd:dark', linestyle='-', lw=0.8)
ax.set_ylabel('Amplitude Ratio (24-H / 12-H)' , fontsize=22, labelpad= 7)
plt.xticks(range(1, 13))
ax.set_xticklabels(months)
ax.tick_params(axis="both", which="major", labelsize=18)
plt.grid(alpha=0.25)
plt.legend(fontsize=15,  framealpha=0)

plt.tight_layout()
