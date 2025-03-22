
from src.geography_input.elevation_extraction import get_srtm_elevation_data
from src.geography_input.water_extraction import get_lakes_with_area
from src.visualization.plot_geography import visualize_topography_with_lakes
from src.spacial.geo_coord_sys import GeoBoundingBox, crop_bounding_box_to_ratio
from src.contour_calculation.topographic_contours import get_contours
from src.contour_calculation.loop_closer import merge_all_loop_fragments
import numpy as np
import numpy.typing as npt
from src.visualization.visualize_contour import dump_contour_image, dump_multiple_contour_images
from src.spacial.table_dimention import Table_Dimention, get_rotated_table
from src.topography_tree.build_topography_tree import build_topography_tree
from src.topography_tree.tree_elaboration import generate_tree_spiral_path
import logging
import sys
from src.logger import get_logger
from scipy.spatial.distance import euclidean
import os

logger = get_logger("main", logging.DEBUG)


def rotate_points(points, width, height, rotation_degrees):
    """
    Rotate a list of 2D points around the center of the width x height rectangle.
    
    Args:
        points: List of [x, y] points to rotate
        width: Width of the bounding rectangle
        height: Height of the bounding rectangle
        rotation_degrees: Rotation angle in degrees (0, 90, 180, or 270)
        
    Returns:
        List of rotated [x, y] points
    """
    # Convert points to numpy array for easier manipulation
    points_array = np.array(points)
    
    # Center of the rectangle
    center_x = width / 2
    center_y = height / 2
    
    # Translate points to origin (center of the rectangle)
    centered_points = points_array - np.array([center_x, center_y])
    
    # No need for complex rotation matrices since we only have 90° increments
    rotated_points = []
    
    if rotation_degrees == 0:
        # No rotation
        rotated_points = centered_points
    elif rotation_degrees == 90:
        # 90° clockwise rotation: (x, y) -> (-y, x)
        rotated_points = np.column_stack((-centered_points[:, 1], centered_points[:, 0]))
    elif rotation_degrees == 180:
        # 180° rotation: (x, y) -> (-x, -y)
        rotated_points = -centered_points
    elif rotation_degrees == 270:
        # 270° clockwise rotation: (x, y) -> (y, -x)
        rotated_points = np.column_stack((centered_points[:, 1], -centered_points[:, 0]))
    else:
        raise ValueError("Rotation must be 0, 90, 180, or 270 degrees")
    
    # Handle width/height swap for 90° and 270° rotations
    if rotation_degrees in [90, 270]:
        # Swap width and height for the translation back
        center_x, center_y = center_y, center_x
    
    # Translate back from origin
    final_points = rotated_points + np.array([center_x, center_y])
    
    return final_points


def output_gcode(filename: str, path: npt.NDArray[np.float64]):
    try:
        with open(filename, "w") as file:
            for location in path:
                file.write("G01 X{:.3f} Y{:.3f}\n".format(*location))
    except OSError as err:
        logger.fatal("Could not output gcode file '{}': {}".format(filename, err))
        return
    logger.info("Successfully wrote gcode to '{}'".format(filename))


def get_total_length(path: npt.NDArray[np.float64]) -> float:
    total_dist_mm = 0
    for i in range(len(path) - 1):
        total_dist_mm += euclidean(path[i], path[i+1])
    return total_dist_mm


def convert_geography_to_gcode(bbox: GeoBoundingBox, table_dim: Table_Dimention, rotation_deg: int, input_data_paths, output_gcode_filepath: str, num_contours: int = 20, debug_file_dir: str = None):
    
    if debug_file_dir is not None and not os.path.isdir(debug_file_dir):
        logger.debug("Creating directory for images: {}".format(debug_file_dir))
        try:
            os.mkdir(debug_file_dir)
        except OSError as err:
            logger.error("Could not create debug dir '{}'. Skipping debug files: {}".format(err))
            debug_file_dir = None
    
    # Rotate table
    table_dim_rotated = get_rotated_table(table_dim, rotation_deg)
    if table_dim_rotated is None:
        logger.fatal("Could not rotate table {} degrees".format(rotation_deg))
        sys.exit(1)

    # Crop the GeoBBox into the same aspect ratio as the table
    bbox = crop_bounding_box_to_ratio(bbox, table_dim_rotated.get_aspect_ratio())
    
    # Get elevation data
    elevation_data = get_srtm_elevation_data(input_data_paths, bbox)

    # Debug
    logger.debug("Elevation Shape {}".format(elevation_data.shape))
    
    # Get lakes with area information
    lakes_gdf = get_lakes_with_area(bbox)
    
    # Visualize the topography with lakes
    if debug_file_dir is not None:
        visualize_topography_with_lakes(bbox, elevation_data, lakes_gdf, debug_file_dir)
    
    contour_line_paths, contour_fig = get_contours(elevation_data, table_dim_rotated, num_contours)
    
    # Visual debug
    # List List Path
    if debug_file_dir is not None:
        try:
            contour_fig.savefig(os.path.join(debug_file_dir, "topography"), dpi=300)
        except OSError as err:
            logger.error("Failed to save contour plot: {}".format(err))
        dump_multiple_contour_images(debug_file_dir, "contour", contour_line_paths, table_dim_rotated)
    
    contour_loops = merge_all_loop_fragments(contour_line_paths, table_dim_rotated)
    
    # Visual debug
    # List List ContourLoop
    if debug_file_dir is not None:
        dump_multiple_contour_images(debug_file_dir, "defragged_contour", contour_loops, table_dim_rotated)
        
    # Build topography tree
    topo_tree = build_topography_tree(contour_loops, table_dim_rotated)
    
    # Debug
    # topo_tree.pretty_print_tree()
        
    path = generate_tree_spiral_path(table_dim_rotated, topo_tree)
    
    # List Tuple Float
    if debug_file_dir is not None:
        dump_contour_image(os.path.join(debug_file_dir, "complete_path_rotated.png"), path, table_dim_rotated)
    
    # Rotate
    path = rotate_points(path, table_dim_rotated.get_width_mm(), table_dim_rotated.get_height_mm(), rotation_deg)
    
    output_file_basepath = os.path.splitext(output_gcode_filepath)[0]
    
    # Numpy (Nx2)
    dump_contour_image(output_file_basepath + ".png", path, table_dim)
    
    total_dist = get_total_length(path)
    logger.info("Total Distance {:.3f} (m)".format(total_dist/1000))
    
    output_gcode(output_file_basepath+".gcode", path)
    