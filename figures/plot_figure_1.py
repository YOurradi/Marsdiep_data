from matplotlib import pyplot as plt
import numpy as np
from cartopy import crs as ccrs, feature as cfeature
import xarray as xr
# import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

# This script plots the bathymetry maps for the Marsdiep Channel and North Sea regions.

# Load and merge EMODnet bathymetry tiles
def import_emodnet_row(row):
    return xr.merge([
        xr.open_dataset(f"Marsdiep_data/data/emodnet/{row}{col}_2024.nc").elevation
        for col in [4, 5]
    ])
bathy = xr.merge([import_emodnet_row(row) for row in ["D", "E"]])


# Setup colormap
cmap = plt.cm.Blues_r
cmap = plt.cm.colors.ListedColormap(cmap(np.linspace(0.2, 0.75, 256)))
cmap.set_bad('xkcd:dark grey')

# Create figure with GridSpec for different widths
fig = plt.figure(figsize=(20, 12), dpi=300)
gs = GridSpec(1, 2, width_ratios=[1.5, 2], wspace=0.15, figure=fig)  

# gs = GridSpec(2, 2, height_ratios=[1, 2.6], width_ratios=[3.7, 1], hspace=0.25)

# Fisrt subplot: North Sea
ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
bathy1 = bathy.sel(lon=slice(-1, 8), lat=slice(51, 60))
ax1.set_extent([-1, 8, 51, 57], crs=ccrs.PlateCarree())  #60
ax1.set_aspect('auto')

# Plot bathymetry
bathy_water_only1 = bathy1.elevation.where(bathy1.elevation <= 0)
contour1 = ax1.contourf(
    bathy1.lon, 
    bathy1.lat, 
    bathy_water_only1,
    levels=np.arange(-500, 1, 50), 
    cmap=cmap,
    transform=ccrs.PlateCarree()
)

# Add land
ax1.add_feature(cfeature.NaturalEarthFeature(
    "physical", "land", "10m"
), facecolor='xkcd:dark', alpha=0.95)


ax1.add_feature(cfeature.NaturalEarthFeature(
    "physical", "lakes", "10m"
), facecolor='xkcd:very light pink', alpha=1, zorder=4)

ax1.add_feature(cfeature.NaturalEarthFeature(
    "physical", "rivers_lake_centerlines", "10m"
), edgecolor='xkcd:very light pink', alpha=1, facecolor='none', linewidth=1.5, zorder=5)


# Add contour lines
contour_lines1 = ax1.contour(
    bathy1.lon, 
    bathy1.lat, 
    bathy1.elevation, 
    levels=np.arange(-50, 100, 100),
    colors='black', 
    alpha=0.3, 
    linewidths=0.5,
    transform=ccrs.PlateCarree()
)

# Colorbar for first subplot
# cbar1 = plt.colorbar(contour1, ax=ax1, shrink=0.8,  orientation='horizontal', aspect=20, pad=0.02)
# cbar1.set_label('Depth / m', rotation=90, labelpad=15, fontsize=12)

cbar1 = plt.colorbar(contour1, ax=ax1, orientation='horizontal', 
                     fraction=0.046, pad=0.08)
cbar1.set_label('Depth / m', fontsize=15)
cbar1.ax.invert_xaxis()

# Gridlines
gl1 = ax1.gridlines(draw_labels=True, alpha=0.3, linestyle='--')
gl1.xlabel_style = {'size': 15, 'color': 'black'}
gl1.ylabel_style = {'size': 15, 'color': 'black'}
gl1.top_labels = False
gl1.right_labels = False

box = Rectangle(
    (4.4, 52.8),      
    1,              
    0.6,              
    linewidth=4,
    edgecolor='xkcd:nice blue',   
    facecolor='none',         
    linestyle='-',            
    transform=ccrs.PlateCarree(),  
    zorder=10
)
ax1.add_patch(box)

# Second plot: Wadden Sea
ax2 = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())

# Different region of interest for second subplot
bathy2 = bathy.sel(lon=slice(4.2, 5.6), lat=slice(52.8, 53.6))
ax2.set_extent([4.2, 5.6, 52.8, 53.6], crs=ccrs.PlateCarree())
ax2.set_aspect('auto')

# Plot bathymetry
bathy_water_only2 = bathy2.elevation.where(bathy2.elevation <= 0)
contour2 = ax2.contourf(
    bathy2.lon, 
    bathy2.lat, 
    bathy_water_only2,
    levels=np.arange(-80, 1, 20),
    cmap=cmap,
    transform=ccrs.PlateCarree()
)

# Add land
ax2.add_feature(cfeature.NaturalEarthFeature(
    "physical", "land", "10m"
), facecolor='xkcd:dark', alpha=0.95)

ax2.add_feature(cfeature.NaturalEarthFeature(
    "physical", "lakes", "10m"
), facecolor='xkcd:very light pink', alpha=0.9, zorder=4)

ax2.add_feature(cfeature.NaturalEarthFeature(
    "physical", "rivers_lake_centerlines", "10m"
), edgecolor='xkcd:very light pink', alpha=0.9, 
    facecolor='none', linewidth=0.8, zorder=4)

 
# Add contour lines
contour_lines2 = ax2.contour(
    bathy2.lon, 
    bathy2.lat, 
    bathy2.elevation, 
    levels=np.arange(-50, 50, 50),
    colors='black', 
    alpha=0.3, 
    linewidths=0.5,
    transform=ccrs.PlateCarree()
)

# Horizontal colorbar for second subplot
# cbar2 = plt.colorbar(contour2, ax=ax2, orientation='horizontal', 
#                      shrink=0.8, aspect=30, pad=0.08)
# cbar2.set_label('Depth / m', fontsize=12)

cbar2 = plt.colorbar(contour2, ax=ax2, orientation='horizontal', 
                     fraction=0.046, pad=0.08)
cbar2.set_label('Depth / m', fontsize=15)
cbar2.ax.invert_xaxis()

# Gridlines
gl2 = ax2.gridlines(draw_labels=True, alpha=0.25, linestyle='--')
gl2.xlabel_style = {'size': 15, 'color': 'black'}
gl2.ylabel_style = {'size': 15, 'color': 'black'}

gl2.top_labels = False
gl2.right_labels = False

ax1.text(0.4, 0.7, 'North Sea', transform=ax1.transAxes, 
         fontsize=20, fontweight='bold', va='top', ha='left')

ax2.text(0.65, 0.6, 'Wadden Sea', transform=ax2.transAxes, 
         fontsize=20, fontweight='bold', va='top', ha='left')

ax2.text(0.22, 0.25, 'Marsdiep\n Channel', transform=ax2.transAxes, 
         fontsize=15, fontweight='bold', va='top', ha='left')

ax2.text(0.68, 0.05, 'IJsselmeer', transform=ax2.transAxes, 
         fontsize=18, fontweight='bold',c="xkcd:dark", zorder=10, va='top', ha='left') 

# ax2.plot(4.78, 53, marker='*', markersize=25, color='xkcd:bright yellow', 
#          transform=ccrs.PlateCarree(), zorder=10)

ax2.plot(4.78, 53, marker='*', markersize=25, color='xkcd:bright yellow', 
         markeredgecolor='red', markeredgewidth=2,
         transform=ccrs.PlateCarree(), zorder=10)

ax1.text(0.9, 0.95, '(a)', transform=ax1.transAxes, c="xkcd:dark",
         fontsize=20, fontweight='bold', va='top', ha='left')
         

ax2.text(0.93, 0.95, '(b)', transform=ax2.transAxes, c="xkcd:dark",
         fontsize=20, fontweight='bold', zorder=10, va='top', ha='left',
         )

plt.tight_layout()

