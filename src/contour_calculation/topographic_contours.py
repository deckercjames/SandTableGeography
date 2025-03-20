
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np
import numpy.typing as npt
import sys
from typing import List
matplotlib.use('Agg')  # Use the Agg backend
from src.logger import get_logger
import logging
from matplotlib.figure import Figure
from src.spacial.table_dimention import Table_Dimention

logger = get_logger("topography", logging.DEBUG)

def compute_adaptive_levels(elevations, x_line_space, y_line_space, max_distance_mm=10):
    """
    Compute contour levels ensuring maximum spatial distance between contours is <= max_distance
    
    Parameters:
    -----------
    Z : 2D array
        The scalar field to contour
    x_grid, y_grid : 2D arrays
        The x and y coordinates for Z
    max_distance : float
        Maximum allowed distance between adjacent contour lines
        
    Returns:
    --------
    levels : array
        Contour levels that satisfy the maximum distance constraint
    """
    print("Adaptive levels")
    print(elevations.shape)
    print(x_line_space.shape)
    print(y_line_space.shape)
    
    # Compute the gradient magnitude of Z
    # dx, dy = np.gradient(Z, x_grid[0, :], y_grid[:, 0])
    dx, dy = np.gradient(elevations, y_line_space, x_line_space)
    gradient_magnitude = np.sqrt(dx**2 + dy**2)
    
    # Avoid division by zero
    gradient_magnitude = np.where(gradient_magnitude > 0, gradient_magnitude, np.finfo(float).eps)
    
    # Calculate minimum level spacing needed at each point to maintain max_distance
    # max_level_step * 1/|∇Z| = max_distance  =>  max_level_step = max_distance * |∇Z|
    min_level_step = max_distance_mm * np.min(gradient_magnitude)
    
    # For safety, we reduce the step size a bit
    min_level_step *= 0.8
    
    # Create evenly spaced levels based on the minimum step required
    z_min, z_max = np.min(elevations), np.max(elevations)
    num_levels = int(np.ceil((z_max - z_min) / min_level_step)) + 1
    
    print(min_level_step)
    print(z_min, z_max)
    print(num_levels)
    
    sys.exit(1)
    
    levels = np.linspace(z_min, z_max, num_levels)
    
    return levels


def break_apart_sub_loops(contour_lines) -> List[List[Path]]:
    
    all_loops = []
    
    logger.info("Breaking apart sub loops...")
    
    # print("Found contours", len(contour_lines))
    # print(contour_lines[0])
    for j, collection in enumerate(contour_lines.collections):
        
        loops = []
        
        contour_paths = collection.get_paths()
        
        if len(contour_paths) == 0:
            continue
        
        path = contour_paths[0]
        
        vertices = path.vertices
        codes = path.codes
        
        # Find positions where the path has a MOVETO command (code 1)
        # These indicate the start of a new loop
        moveto_indices = np.where(codes == Path.MOVETO)[0]
        
        # Extract each loop
        for i in range(len(moveto_indices)):
            start_idx = moveto_indices[i]
            # End index is either the next MOVETO or the end of the array
            end_idx = moveto_indices[i+1] if i+1 < len(moveto_indices) else len(vertices)
            
            # Create a new path for this loop
            loop_vertices = vertices[start_idx:end_idx]
            loop_codes = codes[start_idx:end_idx]
            loop_path = Path(loop_vertices, loop_codes)
            
            loops.append(loop_path)
            
        all_loops.append(loops)

    logger.info("Finished breaking apart sub loops")

    return all_loops
        

def get_const_levels(elevation_data, interval):
    min_elev = np.floor(elevation_data.min() / interval) * interval
    max_elev = np.ceil(elevation_data.max() / interval) * interval
    return np.arange(min_elev, max_elev + interval, interval)


def get_contours(elevation_data: npt.NDArray[np.float64], table_dim_rotated: Table_Dimention) -> tuple[List[List[Path]], Figure]:
    
    x_line_space = np.linspace(0, table_dim_rotated.get_width_mm(), elevation_data.shape[1], dtype=np.float64)
    y_line_space = np.linspace(table_dim_rotated.get_height_mm(), 0, elevation_data.shape[0], dtype=np.float64)

    # TODO this doesn't work if there is any really flat terrain
    # levels = compute_adaptive_levels(elevations, x_line_space, y_line_space)
    levels = get_const_levels(elevation_data, 20)
    
    # Plot contour lines
    fig, ax = plt.subplots()
    contour_lines = ax.contour(x_line_space, y_line_space, elevation_data, levels=levels)
    ax.set_aspect('equal')
    
    contour_lines = break_apart_sub_loops(contour_lines)
    
    return contour_lines, fig
