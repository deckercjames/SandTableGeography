

from src.geography.geo_coord_sys import GeoCoord, GeoBoundingBox
from PIL import Image, ImageDraw
from matplotlib.path import Path
from typing import List, Union
from src.utils import Table_Dimention
from src.geography.contour_calculation.contour_loop import ContourLoop
import numpy as np
import os
from src.logger import get_logger
import logging

logger = get_logger("visualize", logging.DEBUG)


def _draw_line(img_draw: ImageDraw, location0, location1, color, height, scale, buffer):
    x0, y0 = location0
    x1, y1 = location1
    
    x0 = int((x0 * scale) + buffer)
    y0 = int((y0 * scale) + buffer)
    x1 = int((x1 * scale) + buffer)
    y1 = int((y1 * scale) + buffer)
    
    img_draw.line((x0, height - y0, x1, height - y1), fill=color)


def dump_contour(img_draw: ImageDraw, contour_path: Union[Path, ContourLoop], height: int, scale: float, buffer: int):
    
    if type(contour_path) is Path:
        path_vertices = contour_path.vertices
    elif type(contour_path) is ContourLoop:
        path_vertices = contour_path.vertices
    elif type(contour_path) is list:
        path_vertices = contour_path
    elif type(contour_path) is np.ndarray:
        path_vertices = contour_path
    else:
        raise Exception("Unexpected type {}".format(type(contour_path)))
    
    for i in range(len(path_vertices) - 1):
        
        color = (
            255,
            int((1 - (i / len(path_vertices))) * 255),
            0
        )
        
        _draw_line(img_draw, path_vertices[i], path_vertices[i+1], color, height, scale, buffer)
        
    # ContourLoop do not close them selves
    if type(contour_path) is ContourLoop:
        _draw_line(img_draw, path_vertices[0], path_vertices[-1], 'red', height, scale, buffer)
        sx, sy = contour_path.get_sample_vertex()
        ELLIPSE_SIZE = 5 * scale
        bounds = (
            sx - ELLIPSE_SIZE + buffer,
            height - (sy + ELLIPSE_SIZE + buffer),
            sx + ELLIPSE_SIZE + buffer,
            height - (sy - ELLIPSE_SIZE + buffer),
        )
        img_draw.ellipse(bounds, fill=(0, 255, 255))
    

def dump_contour_image(debug_image_dir: str, image_name: str, contours: List[Path], table_dim: Table_Dimention):
    
    if not os.path.isdir(debug_image_dir):
        logger.debug("Creating directory for images: {}".format(debug_image_dir))
        os.mkdir(parents=True)
    
    SCALE = 1 # pixels per mm
    BUFFER = int(5 * SCALE)
    
    width = int(table_dim.get_width_mm() * SCALE) + BUFFER + BUFFER
    height = int(table_dim.get_height_mm() * SCALE) + BUFFER + BUFFER
    
    img = Image.new("RGB", (width, height))
    img_draw = ImageDraw.Draw(img)
    
    if type(contours[0]) is Path or type(contours[0]) is ContourLoop:
        for contour in contours:
            dump_contour(img_draw, contour, height, SCALE, BUFFER)
    else:
        dump_contour(img_draw, contours, height, SCALE, BUFFER)
    
    img.save(os.path.join("{}.png".format(image_name)))


def dump_multiple_contour_images(debug_image_dir: str, image_base_name: str, contours: List, table_dim: Table_Dimention):
    
    for i, item in enumerate(contours):
        dump_contour_image("{}_{}".format(debug_image_dir, image_base_name, i), item, table_dim)