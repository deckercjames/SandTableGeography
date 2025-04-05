
from src.geography_input.elevation_extraction import get_srtm_elevation_data
from src.geography_input.water_extraction import get_lakes_with_area
from src.visualization.plot_geography import visualize_topography_with_lakes
from src.spacial.geo_coord_sys import GeoBoundingBox, crop_bounding_box_to_ratio
from src.contour_calculation.topographic_contours import get_contours
from src.contour_calculation.loop_closer import merge_all_loop_fragments
from src.visualization.visualize_contour import dump_contour_image, dump_multiple_contour_images
from src.spacial.table_dimention import Table_Dimention
from src.topography_tree.build_topography_tree import build_topography_tree
from src.topography_tree.tree_elaboration import generate_tree_spiral_path
import logging
import sys
from src.logger import get_logger
import os
from src.path_post_processing.path_utils import get_total_length
import numpy.typing as npt
import numpy as np
from src.path_post_processing.path_mask import crop_path_to_circle

logger = get_logger("main", logging.DEBUG)


def get_elevation_data(bbox: GeoBoundingBox, table_dim: Table_Dimention, input_data_paths: str, rotation_deg: int, debug_file_dir: str = None) -> npt.NDArray[np.float64]:
    
    geo_sample_aspect_ratio = table_dim.get_aspect_ratio()
    if rotation_deg in {90, 270}:
        geo_sample_aspect_ratio = 1 / geo_sample_aspect_ratio
    
    # Crop the GeoBBox into the same aspect ratio as the table
    bbox = crop_bounding_box_to_ratio(bbox, geo_sample_aspect_ratio)
    
    # Get elevation data
    elevation_data = get_srtm_elevation_data(input_data_paths, bbox)

    # Debug
    logger.debug("Elevation Shape {}".format(elevation_data.shape))
    
    # Get lakes with area information
    lakes_gdf = get_lakes_with_area(bbox)
    
    # Visualize the topography with lakes
    if debug_file_dir is not None:
        visualize_topography_with_lakes(bbox, elevation_data, lakes_gdf, debug_file_dir)
        
    elevation_data = np.rot90(elevation_data, k=(rotation_deg // 90))
    
    return elevation_data


def convert_elevation_data_to_path(elevation_data: npt.NDArray[np.float64], table_dim: Table_Dimention, num_contours: int = 20, debug_file_dir: str = None) -> npt.NDArray[np.float64]:

    if debug_file_dir is not None and not os.path.isdir(debug_file_dir):
        logger.debug("Creating directory for images: {}".format(debug_file_dir))
        try:
            os.mkdir(debug_file_dir)
        except OSError as err:
            logger.error("Could not create debug dir '{}'. Skipping debug files: {}".format(err))
            debug_file_dir = None

    contour_line_paths, contour_fig = get_contours(elevation_data, table_dim, num_contours)
    
    # Visual debug
    # List List Path
    if debug_file_dir is not None:
        try:
            contour_fig.savefig(os.path.join(debug_file_dir, "topography"), dpi=300)
        except OSError as err:
            logger.error("Failed to save contour plot: {}".format(err))
        dump_multiple_contour_images(debug_file_dir, "contour", contour_line_paths, table_dim)
    
    contour_loops = merge_all_loop_fragments(contour_line_paths, table_dim)
    
    # Visual debug
    # List List ContourLoop
    if debug_file_dir is not None:
        dump_multiple_contour_images(debug_file_dir, "defragged_contour", contour_loops, table_dim)
        
    # Build topography tree
    topo_tree = build_topography_tree(contour_loops, table_dim)
    
    # Debug
    # topo_tree.pretty_print_tree()
        
    path = generate_tree_spiral_path(topo_tree)
    
    if table_dim.is_circular():
        path = crop_path_to_circle(path, table_dim)
    
    return path
    
    
def convert_geography_to_gcode(bbox: GeoBoundingBox, table_dim: Table_Dimention, rotation_deg: int, input_data_paths: str, output_gcode_filepath: str, num_contours: int = 20, debug_file_dir: str = None):
    
    elevation_data = get_elevation_data(bbox, table_dim, input_data_paths, rotation_deg, debug_file_dir=debug_file_dir)
    
    path = convert_elevation_data_to_path(elevation_data, table_dim, num_contours=num_contours, debug_file_dir=debug_file_dir)
    
    # Get the basename of the output file path
    output_file_basepath, output_file_ext = os.path.splitext(output_gcode_filepath)
    if output_file_ext != ".gcode":
        output_file_basepath += output_file_ext
    
    # Numpy (Nx2)
    dump_contour_image(output_file_basepath + ".png", path, table_dim)
    
    total_dist_meters = get_total_length(path) / 1000
    logger.info("Total Distance {:.3f} (m)".format(total_dist_meters))
    
    # Write output gcode file
    output_gcode_filepath = output_file_basepath + ".gcode"
    try:
        with open(output_gcode_filepath, "w") as file:
            file.write(";\n")
            file.write("; Topographic Map\n")
            if table_dim.is_circular():
                file.write("; Table Diameter (millimeters): {}\n".format(table_dim.get_width_mm()))
            else:
                file.write("; Rectangular Table Shape (millimeters): {} x {}\n".format(table_dim.get_width_mm(), table_dim.get_height_mm()))
            file.write("; Latitude:  [{:.06f}, {:.06f}]\n".format(bbox.get_min_lat(), bbox.get_max_lat()))
            file.write("; Longitude: [{:.06f}, {:.06f}]\n".format(bbox.get_min_lon(), bbox.get_max_lon()))
            file.write("; Total Path Distance (meters): {:.3f}\n".format(total_dist_meters))
            file.write("; North is to the {}\n".format({0:"top", 90:"left", 180:"bottom", 270:"right"}[rotation_deg]))
            file.write(";\n\n")
            for location in path:
                file.write("G01 X{:.3f} Y{:.3f}\n".format(*location))
    except OSError as err:
        logger.fatal("Could not output gcode file '{}': {}".format(output_gcode_filepath, err))
        sys.exit(1)

    logger.info("Successfully wrote gcode to '{}'".format(output_gcode_filepath))
