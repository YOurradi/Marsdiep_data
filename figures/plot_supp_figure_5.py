import matplotlib.pyplot as plt
import pandas as pd
# import matplotlib.cm as cm
# import PyCO2SYS as pyco2

# This script plots the gas transfer velocity


# Import data
data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")
data['datetime'] = pd.to_datetime(data['datetime'])

fig, (ax) = plt.subplots(dpi=600, figsize=(20,8))

ax.fill_between(data.datetime, data.k_Ni00, color='xkcd:sea blue', alpha=0.8, lw=2)
ax.set_ylim(0,100)

ax.grid(alpha=0.25)
ax.set_ylabel('kw / cm.h⁻¹', fontsize=25)
ax.set_xlim(pd.Timestamp('2022-01-30'), pd.Timestamp('2023-01-13'))
ax.tick_params(axis='both', labelsize=22)
plt.xticks(rotation=45)

