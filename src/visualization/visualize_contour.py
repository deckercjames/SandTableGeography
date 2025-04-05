

from PIL import Image, ImageDraw
from matplotlib.path import Path
from typing import List, Union
from src.spacial.table_dimention import Table_Dimention
from src.contour_calculation.contour_loop import ContourLoop
import numpy as np
import os
from src.logger import get_logger
import logging

logger = get_logger("visualize", logging.DEBUG)


def draw_contour_on_image(img_draw: ImageDraw, contour_path: Union[Path, ContourLoop], height_mm: int, scale: float, buffer: int):
    
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
        
        x0, y0 = path_vertices[i]
        x1, y1 = path_vertices[i+1]
        
        x0 = int((x0 + buffer) * scale)
        y0 = int((height_mm - y0 + buffer) * scale)
        x1 = int((x1 + buffer) * scale)
        y1 = int((height_mm - y1 + buffer) * scale)
        
        img_draw.line((x0, y0, x1, y1), fill=color, width = (scale // 2))
    

def dump_contour_image(image_name: str, contours: List[Path], table_dim: Table_Dimention):
    
    SCALE = 8 # pixels per mm
    BUFFER = 5 # buffer in mm
    
    width = int(table_dim.get_width_mm() + BUFFER + BUFFER) * SCALE
    height = int(table_dim.get_height_mm() + BUFFER + BUFFER) * SCALE
    
    img = Image.new("RGB", (width, height))
    img_draw = ImageDraw.Draw(img)
    
    if type(contours[0]) is Path or type(contours[0]) is ContourLoop:
        for contour in contours:
            draw_contour_on_image(img_draw, contour, table_dim.get_height_mm(), SCALE, BUFFER)
    else:
        draw_contour_on_image(img_draw, contours, table_dim.get_height_mm(), SCALE, BUFFER)
    
    try:
        img.save(image_name)
    except OSError as err:
        logger.error("Could not write contour image: {}".format(err))


def dump_multiple_contour_images(debug_image_dir: str, image_base_name: str, contours: List, table_dim: Table_Dimention):
    
    for i, item in enumerate(contours):
        dump_contour_image("{}_{}.png".format(os.path.join(debug_image_dir, image_base_name), i), item, table_dim)