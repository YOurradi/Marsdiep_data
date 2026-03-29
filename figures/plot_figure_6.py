import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd

# This scripts plots the regressions between TA and Salinity, and combining
# the months together whenever the fit is better.


# Import data
all_data = pd.read_parquet("Marsdiep_data/data/all_jetty_results.parquet")
all_data["month"] = all_data["datetime"].dt.month

# No data in November
all_data = all_data[all_data["month"] != 11]

L = all_data["alkalinity"].notnull()
all_data = all_data[L]

# Dividing the months by groups
# group_1 = all_data[all_data['month'].isin([12, 1])]
group_1 = all_data[all_data["month"].isin([12, 1, 2, 3])]
# group_2 = all_data[all_data['month'].isin([2, 3])]
group_3 = all_data[all_data["month"].isin([7, 8])]
group_4 = all_data[all_data["month"].isin([9, 10])]


# Calcualting the regression lines
def plot_regression_line(group, ax, color, label):
    group = group[["salinity", "alkalinity"]].dropna()
    if len(group) == 0:
        return
    X = group["salinity"].values.reshape(-1, 1)
    y = group["alkalinity"].values
    reg = LinearRegression().fit(X, y)
    y_pred = reg.predict(X)
    ax.plot(group["salinity"], y_pred, color=color, label=label, linewidth=1.1)

    slope = reg.coef_[0]
    intercept = reg.intercept_
    r2 = reg.score(X, y)
    return slope, intercept, r2


group_regression_results = {}

# Making the plot
fig, ax = plt.subplots(figsize=(7,5), dpi=600)
sc = ax.scatter(
    all_data["salinity"],
    all_data["alkalinity"],
    s=10,
    c=all_data["month"],
    cmap="twilight_shifted",
)

# cbar = plt.colorbar(sc)
# cbar.set_label("Month", fontsize=7)

month_names = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
# cbar.set_ticks(range(1, 13))
# cbar.set_ticklabels(month_names, fontsize=6)

ax.set_xlabel("Salinity", fontsize=10, labelpad=7)
ax.set_ylabel("TA/ μmol.kg⁻¹", fontsize=10, labelpad=7)
ax.tick_params(axis="both", which="major", labelsize=9)
ax.set_ylim(2300, 2500)
# plt.xticks(rotation=45)

# Choosing the colormap and the number of colors to use
cmap = plt.get_cmap("twilight_shifted")
norm = plt.Normalize(1, 13)

# The regressions lines by order
grouped_months = [12, 1, 2, 3, 7, 8, 9, 10]
plot_regression_line(group_1, ax, color=cmap(norm(12)), label="Dec-Mar")
# plot_regression_line(group_2, ax, color=cmap(norm(2)), label='Feb-Mar')

for month, group in all_data.groupby("month"):
    if month not in grouped_months:
        color = cmap(norm(month))
        plot_regression_line(group, ax, color=color, label=f"{month_names[month - 1]}")

plot_regression_line(group_3, ax, color=cmap(norm(7)), label="Jul-Aug")
plot_regression_line(group_4, ax, color=cmap(norm(8)), label="Sep-Oct")

plt.legend(bbox_to_anchor=(1.2, 1), fontsize=7)
ax.grid(alpha=0.25)


