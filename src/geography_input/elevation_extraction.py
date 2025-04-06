import numpy as np
import numpy.typing as npt
import sys
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box
import os
from pathlib import Path
import tempfile
from typing import List, Union
from src.spacial.geo_coord_sys import GeoBoundingBox
from src.logger import get_logger
import logging

logger = get_logger("elevation import", logging.DEBUG)


def _normalize_file_path(srtm_files: Union[str, List[str]]) -> List[str]:
    """
    Converts either a single file, list of files, or directory, into a list
    of files. Direcotries are expanded to all tif/hgt files inside of it.
    A single file path is converted into a list of length 1, containing it
    """
    if isinstance(srtm_files, list):
        return srtm_files
    
    # Convert single file to list
    if os.path.isfile(srtm_files):
        return [srtm_files]
    
    # Convert directory to list
    if os.path.isdir(srtm_files):
        # If directory, get all tif and hgt files in the directory
        path = Path(srtm_files)
        srtm_files = list(path.glob("*.tif")) + list(path.glob("*.hgt"))
        return [str(file) for file in srtm_files]
        
    logger.fatal("Could not find any .tif or .hgt files from: {}".format(srtm_files))
    sys.exit(1)


def _load_and_crop_data_from_file(srtm_file_path: str, bbox: GeoBoundingBox):
    with rasterio.open(srtm_file_path) as src:
        
        # Verify that the file has full coverage of the bounds
        file_bounds = src.bounds
        if (bbox.get_min_lon() < file_bounds.left or bbox.get_max_lon() > file_bounds.right or
                    bbox.get_min_lat() < file_bounds.bottom or bbox.get_max_lon() > file_bounds.top):
            logger.fatal("Given elevation data does not cover requested bounding box")
            sys.exit(1)
        
        # Create a geometry from the bounds
        geom = [box(*bbox.get_all_values_tuple())]
        
        # Mask the dataset to the geometry
        try:
            elevation_data, _ = mask(src, geom, crop=True, all_touched=True)
            elevation_data = elevation_data[0]  # Get the first band
        except ValueError:
            logger.fatal("Merged bounds issue.")
            sys.exit(1)

    logger.debug("Loaded file: {}".format(srtm_file_path))
    return elevation_data


def _filter_relevent_files(srtm_files, bbox: GeoBoundingBox):
    
    # First, check if any of the files intersect with our bounds
    files_to_process = []

    # Check each file against the bounds
    for file_path in srtm_files:
        try:
            with rasterio.open(file_path) as src:
                file_bounds = src.bounds
                
                # Check if file bounds intersect with requested bounds
                if (bbox.get_min_lon() < file_bounds.right and bbox.get_max_lon() > file_bounds.left and
                    bbox.get_min_lat() < file_bounds.top and bbox.get_max_lat() > file_bounds.bottom):
                    files_to_process.append(file_path)
        except OSError as err:
            logger.warning("Could not open '{}' Error: {}".format(file_path, err))
    
    return files_to_process


def _load_data(files_to_process, bounds):
    
    if len(files_to_process) == 1:
        return _load_and_crop_data_from_file(files_to_process[0], bounds)
    
    # Process files sequentially using temporary files
    # Create a temporary directory for intermediate merges
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "merged.tif")
        
        # Start with the first file
        current_file = files_to_process[0]
        with rasterio.open(current_file) as src:
            meta = src.meta.copy()
            # Read the first band 
            data = src.read(1)
            
            # Write to temporary file
            meta.update({
                "driver": "GTiff", 
                "height": data.shape[0], 
                "width": data.shape[1],
            })
            with rasterio.open(temp_file, 'w', **meta) as dst:
                dst.write(data, 1)
        
        # Process remaining files
        for i in range(1, len(files_to_process)):
            try:
                # Open current merged file and next file to merge
                with rasterio.open(temp_file) as src1, rasterio.open(files_to_process[i]) as src2:
                    # Merge the datasets
                    mosaic, out_transform = merge([src1, src2])
                    
                    # Update metadata
                    meta = src1.meta.copy()
                    meta.update({
                        "driver": "GTiff",
                        "height": mosaic.shape[1],
                        "width": mosaic.shape[2],
                        "transform": out_transform,
                    })
                    
                    # Write to a new temporary file
                    new_temp = os.path.join(temp_dir, f"merged_{i}.tif")
                    with rasterio.open(new_temp, 'w', **meta) as dst:
                        dst.write(mosaic)
                    
                    # Replace the old temp file
                    os.replace(new_temp, temp_file)
            except Exception as e:
                logger.warning("Error processing file {}: {}".format(files_to_process, e))
        
        # Read the final merged result
        return _load_and_crop_data_from_file(temp_file, bounds)



def get_srtm_elevation_data(srtm_files, bbox: GeoBoundingBox) -> npt.NDArray[np.float64]:
    """
    Extract elevation data from multiple SRTM data files using rasterio.
    Files are processed sequentially to minimize memory usage.
    
    Parameters:
    -----------
    srtm_files : list or str
        List of paths to SRTM data files (.tif or .hgt format),
        or path to a directory containing SRTM files,
        or a single file path.
    bbox : GeoBoundingBox
        Bounding box to get data for
    
    Returns:
    --------
    npt.NDArray[np.float64]
    """
    norm_srtm_files = _normalize_file_path(srtm_files)
    
    logger.info("Found {} elevation files from path '{}'".format(len(norm_srtm_files), srtm_files))

    files_to_process = _filter_relevent_files(norm_srtm_files, bbox)
    
    if len(files_to_process) == 0:
        logger.fatal("None of the provided files intersect with the specified bounds.")
        sys.exit(1)

    logger.info("Found {} relevant elevation files".format(len(files_to_process)))
    
    elevation_data = _load_data(files_to_process, bbox)

    logger.info("Successfully loaded all necessary elevation data")
    
    return elevation_data