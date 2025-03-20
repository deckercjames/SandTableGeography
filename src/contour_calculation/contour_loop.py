
from __future__ import annotations
import numpy as np
import numpy.typing as npt
from shapely.geometry import Polygon, Point
from src.table_dimention import Table_Dimention
import math
from matplotlib.path import Path

class ContourLoop:
    def __init__(self, vertices, sample_vertex=None, border_indices=[]):
        self.vertices = vertices
        if type(self.vertices) is list:
            self.vertices = np.array(self.vertices)
        self.sample_vertex = sample_vertex
        if self.sample_vertex is None:
            self.sample_vertex = vertices[len(vertices) // 2]
        self.polygon = Polygon(vertices)
        self.border_indices = border_indices

    def get_sample_vertex(self):
        return self.sample_vertex
    
    def get_vertices(self):
        return self.vertices
    
    def touches_border(self) -> bool:
        return len(self.border_indices) > 0
    
    def get_border_indices(self):
        return self.border_indices
    
    def contains(self, point: npt.NDArray[np.float64]):
        return self.polygon.contains(Point(*point))
    
    def __eq__(self, other: ContourLoop):
        return np.allclose(self.vertices, other.vertices) and set(self.border_indices) == set(other.border_indices)
    
    def __str__(self):
        return "ContourLoop length {}".format(len(self.vertices))


def get_border_contour_loop(table_dim: Table_Dimention) -> ContourLoop:
    return ContourLoop(
        [
            (0, 0),
            (0, table_dim.get_height_mm()),
            (table_dim.get_width_mm(), table_dim.get_height_mm()),
            (table_dim.get_width_mm(), 0),
        ],
        border_indices=[0, 1, 2, 3]
    )

    
class ContourLoopBuilder:
    def __init__(self, table_dim: Table_Dimention):
        self.table_dim = table_dim
        self.sample_point = None
        self.path = []

    
    def _extend_corner_links(self, location0, location1) -> list:
        corner_points = []
        bp0 = self.table_dim.get_border_position(location0)
        bp1 = self.table_dim.get_border_position(location1)
        x0, y0 = location0
        x1, y1 = location1
        while not (math.isclose(x0, x1) or math.isclose(y0, y1)) or bp0 > bp1:
            # move location_0 clockwise around the border
            on_left   = math.isclose(x0, 0)
            on_top    = math.isclose(y0, self.table_dim.get_height_mm())
            on_right  = math.isclose(x0, self.table_dim.get_width_mm())
            on_bottom = math.isclose(y0, 0)
            if on_left and not on_top:
                y0 = self.table_dim.get_height_mm()
            elif on_top and not on_right:
                x0 = self.table_dim.get_width_mm()
            elif on_right and not on_bottom:
                y0 = 0
            elif on_bottom and not on_left:
                x0 = 0
            else:
                raise Exception("Border walk failed")
            bp0 = self.table_dim.get_border_position((x0, y0))
            corner_points.append((x0, y0))
        self.path.extend(corner_points)

    
    def append_path_frag(self, path: Path):
        
        if len(self.path) > 0:
            self._extend_corner_links(self.path[-1], path.vertices[0])
            
        if self.sample_point is None:
            self.sample_point = path.vertices[len(path.vertices) // 2]
        
        self.path.extend(path.vertices)
        
        
    def get_contour_loop(self) -> ContourLoop:
        if len(self.path) == 0:
            raise Exception("Has not been built")
        
        # close loop
        self._extend_corner_links(self.path[-1], self.path[0])
        
        # find border points
        border_indices = []
        for i, location in enumerate(self.path):
            if not self.table_dim.on_border_float(location):
                continue
            border_indices.append(i)
        
        return ContourLoop(
            self.path,
            sample_vertex=self.sample_point,
            border_indices=border_indices,
        )