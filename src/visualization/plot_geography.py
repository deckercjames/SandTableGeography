import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib import cm
from src.spacial.geo_coord_sys import GeoBoundingBox
matplotlib.use('Agg')  # Use the Agg backend
import cartopy.crs as ccrs
from src.logger import get_logger
import os
import logging

logger = get_logger("geo plot", logging.DEBUG)

def plot_topography_contours(lons_line_space, lats_line_space, elevation_data, bbox, interval=40, ax=None, 
                           colors='black', linewidths=0.8):
    """
    Plot topographic contour lines from elevation data.
    
    Parameters:
    - elevation_data: tuple of (lons_grid, lats_grid, elevations)
    - bbox: tuple of (min_lon, min_lat, max_lon, max_lat)
    - interval: contour interval in meters (default 20m)
    - ax: matplotlib axes to plot on (optional)
    - labels: whether to add elevation labels to contour lines
    - colors: color of contour lines
    - linewidths: width of contour lines
    
    Returns:
    - ax: matplotlib axes with contour plot
    - contour_lines: contour line collection for further customization
    """
    
    # Create a new figure if no axes provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))
    
    # Calculate contour levels based on min/max elevation and interval
    min_elev = np.floor(elevation_data.min() / interval) * interval
    max_elev = np.ceil(elevation_data.max() / interval) * interval
    levels = np.arange(min_elev, max_elev + interval, interval)
    
    # Plot contour lines
    contour_lines = ax.contour(lons_line_space, lats_line_space, elevation_data, 
                             levels=levels, colors=colors, linewidths=linewidths)

    # Set plot bounds to match the bounding box
    ax.set_xlim(bbox[0], bbox[2])
    ax.set_ylim(bbox[1], bbox[3])
    
    # Add labels and title
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Topographic Contour Map')
    
    return contour_lines


def visualize_topography_with_lakes(bbox: GeoBoundingBox, elevation_data: npt.NDArray[np.float64], lakes_gdf, debug_img_dir: str):
    """
    Visualize topography data with lakes and their areas.
    """
    
    # Create geographic lines space
    lons_line_space = np.linspace(bbox.get_min_lon(), bbox.get_max_lon(), elevation_data.shape[1], dtype=np.float64)
    lats_line_space = np.linspace(bbox.get_max_lat(), bbox.get_min_lat(), elevation_data.shape[0], dtype=np.float64)

    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Plot elevation data
    contour = ax.contourf(lons_line_space, lats_line_space, elevation_data, cmap=cm.terrain, levels=20)
    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_label('Elevation (m)')
    
    # Add topographic contour lines
    plot_topography_contours(lons_line_space, lats_line_space, elevation_data, bbox.get_all_values_tuple(), interval=50, 
                           ax=ax, colors='black', linewidths=0.5)

    # Plot lakes
    if not lakes_gdf.empty:
        lakes_gdf.plot(ax=ax, color='magenta')
        
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Topography with Lakes')
    ax.set_xlim(bbox.get_min_lon(), bbox.get_max_lon())
    ax.set_ylim(bbox.get_min_lat(), bbox.get_max_lat())
    
    if debug_img_dir:
        try:
            fig.savefig(os.path.join(debug_img_dir, "geography.png"), dpi=300)
        except OSError as err:
            logger.error("Failed to save geography plot: {}".format(err))
