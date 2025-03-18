
from copy import deepcopy
from typing import List
import numpy as np
from dataclasses import dataclass
import math

@dataclass(eq=True, frozen=True)
class Table_Position:
    x_mm: float
    y_mm: float

@dataclass(eq=True, frozen=True)
class Pixel_Location:
    x: int
    y: int
    
@dataclass(eq=True, frozen=True)
class Table_Dimention:
    width_mm: int
    height_mm: int
    def get_width_mm(self) -> int:
        return self.width_mm
    def get_height_mm(self) -> int:
        return self.height_mm
    def contians_pos(self, pos: Table_Position) -> bool:
        """
        Returns true if the position is on the table 9including the edges
        """
        return pos.x_mm >= 0 and pos.x_mm <= self.width_mm and \
                pos.y_mm >= 0 and pos.y_mm <= self.height_mm
    
    def on_border(self, pos: Table_Position) -> bool:
        return pos.x_mm == 0 or pos.x_mm == self.width_mm or \
                pos.y_mm == 0 or pos.y_mm == self.height_mm
    
    def on_border_float(self, location: tuple[float, float]) -> bool:
        x, y = location
        return math.isclose(x, 0) or math.isclose(x, self.get_width_mm()) or \
                math.isclose(y, 0) or math.isclose(y, self.get_height_mm())
    
    def get_border_position(self, location) -> float:
        x0, y0 = location
        on_left   = math.isclose(x0, 0)
        on_top    = math.isclose(y0, self.get_height_mm())
        on_right  = math.isclose(x0, self.get_width_mm())
        on_bottom = math.isclose(y0, 0)
        pos = 0
        if on_left:
            pos += y0
            return pos
        pos += self.get_height_mm()
        if on_top:
            pos += x0
            return pos
        pos += self.get_width_mm()
        if on_right:
            pos += (self.get_height_mm() - y0)
            return pos
        pos += self.get_height_mm()
        if not on_bottom:
            raise Exception("Point is not on border")
        pos += (self.get_width_mm() - x0)
        return pos

    
class UnitManager:
    def __init__(self, img_width_px: int, img_height_px: int, table_width_mm: int, table_height_mm:int=None):
        self.img_width_pix = img_width_px
        self.img_height_pix = img_height_px
        # Set table dimentions
        if table_height_mm is None:
            table_height_mm = int((table_width_mm * img_height_px) / img_width_px)
        self.table_dim = Table_Dimention(
            table_width_mm, table_height_mm
        )
    def get_table_dim(self) -> Table_Dimention:
        return self.table_dim
    def pix_location_to_position(self, pixel_location: Pixel_Location) -> Table_Position:
        return Table_Position(
            x_mm=(pixel_location.x * self.table_dim.get_width_mm()) / self.img_width_pix,
            y_mm=self.table_dim.get_height_mm() - ((pixel_location.y * self.table_dim.get_height_mm()) / self.img_height_pix),
        )
    

def get_list_element_cyclic(list, i):
    return list[i % len(list)]


def get_neighbor_points(r: int, c: int) -> List[tuple[int, int]]:
    return [
        (r-1, c  ),
        (r-1, c+1),
        (r,   c+1),
        (r+1, c+1),
        (r+1, c  ),
        (r+1, c-1),
        (r,   c-1),
        (r-1, c-1),
    ]


def check_grid_element_safe(grid, r, c, default=None):
    if r < 0 or r >= len(grid):
        return default
    if c < 0 or c >= len(grid[r]):
        return default
    return grid[r][c]


def check_numpy_grid_element_safe(numpy_grid, r, c, default=None):
    if r < 0 or r >= numpy_grid.shape[0]:
        return default
    if c < 0 or c >= numpy_grid.shape[1]:
        return default
    return numpy_grid[r, c]


def get_grid_mask_subtraction(grid_mask, grid_mask_subtrahend):
    if len(grid_mask) != len(grid_mask_subtrahend) or len(grid_mask[0]) != len(grid_mask_subtrahend[0]):
        raise Exception("Can not subtract different sized masks. ({}x{}) - ({}x{})".format(len(grid_mask), len(grid_mask[0]), len(grid_mask_subtrahend), len(grid_mask_subtrahend[0])))

    return [[(grid_mask[r][c] and not grid_mask_subtrahend[r][c]) for c in range(len(grid_mask[r]))] for r in range(len(grid_mask))]


def get_numpy_grid_mask_subtraction(grid_mask, grid_mask_subtrahend):
    return np.logical_and(grid_mask, np.logical_not(grid_mask_subtrahend))


def get_all_false_mask(num_rows, num_cols):
    return [[False for _ in range(num_cols)] for _ in range(num_rows)]


def get_grid_mask_union(m1, m2):
    if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
        raise Exception("Can not union different sized masks. ({}x{}) U ({}x{})".format(len(m1), len(m1[0]), len(m2), len(m2[0])))

    return [[(m1[r][c] or m2[r][c]) for c in range(len(m1[r]))] for r in range(len(m1))]

def get_numpy_grid_mask_union(m1, m2):
    # TODO improve
    return np.logical_or(m1, m2, out=m1)


def get_cyclic_list_slice(list, start_idx, end_idx):
    if end_idx > start_idx:
        return list[start_idx:end_idx]
    return list[start_idx:] + list[:end_idx]


def grid_mask_to_str(grid_mask):
    buf = ""
    buf += "+" + "-" * len(grid_mask[0]) + "+\n"
    for row in grid_mask:
        buf += "|"
        for cell in row:
            buf += "#" if cell else " "
        buf += "|\n"
    buf += "+" + "-" * len(grid_mask[0]) + "+\n"
    return buf


def check_mask_intersection(m1, m2):
    if len(m1) != len(m2):
        raise Exception("Can not subtract different sized masks")
    if len(m1[0]) != len(m2[0]):
        raise Exception("Can not subtract different sized masks")
    
    for r in range(len(m1)):
        for c in range(len(m1[0])):
            if m1[r][c] and m2[r][c]:
                return True
    return False
    

# TODO these functions are the same lol
def get_numpy_mask_with_inward_bleed(grid_mask, diag_bleed=False):
    result = grid_mask.copy()
    
    for r, c in np.ndindex(grid_mask.shape):
        if r == 0 or r == grid_mask.shape[0] - 1 or c == 0 or c == grid_mask.shape[1] - 1:
            result[r][c] = False
            continue
        if not grid_mask[r-1][c] or not grid_mask[r+1][c] or not grid_mask[r][c-1] or not grid_mask[r][c+1]:
            result[r][c] = False
            continue
        if diag_bleed and (not grid_mask[r-1][c+1] or not grid_mask[r+1][c+1] or not grid_mask[r+1][c-1] or not grid_mask[r-1][c-1]):
            result[r][c] = False
            continue
            
    return result


def get_simple_erosion(grid_mask):
    
    result = grid_mask.copy()
    
    for r, c in np.ndindex(grid_mask.shape):
        if not grid_mask[r, c]:
            continue
        if not check_numpy_grid_element_safe(grid_mask, r+1, c, default=False) or not check_numpy_grid_element_safe(grid_mask, r-1, c, default=False) or not check_numpy_grid_element_safe(grid_mask, r, c+1, default=False) or not check_numpy_grid_element_safe(grid_mask, r, c-1, default=False):
            result[r, c] = False
            
    return result