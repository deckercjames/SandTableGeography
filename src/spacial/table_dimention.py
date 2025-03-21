
from copy import deepcopy
from typing import List
import numpy as np
from dataclasses import dataclass
import math

@dataclass(eq=True, frozen=True)
class Table_Dimention:
    width_mm: int
    height_mm: int
    def get_width_mm(self) -> int:
        return self.width_mm
    def get_height_mm(self) -> int:
        return self.height_mm

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
            raise Exception("Point {} is not on border".format(location))
        pos += (self.get_width_mm() - x0)
        return pos
    
    def get_aspect_ratio(self) -> float:
        return self.width_mm / self.height_mm


def get_rotated_table(table_dim: Table_Dimention, rotation_deg: int) -> Table_Dimention:
    if rotation_deg in (0, 180):
        return table_dim
    if rotation_deg in {90, 270}:
        return Table_Dimention(table_dim.get_height_mm(), table_dim.get_width_mm())
    return None