
import math

class Table_Dimention:
    
    def __init__(self, width_mm: int, height_mm: int, circular: bool = False):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.circular = circular

    def get_width_mm(self) -> int:
        return self.width_mm

    def get_height_mm(self) -> int:
        return self.height_mm
    
    def is_circular(self) -> bool:
        return self.circular

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
    
    @staticmethod
    def create_rect_table(width_mm: int, height_mm: int):
        return Table_Dimention(width_mm, height_mm, circular=False)

    @staticmethod
    def create_circular_table(diameter_mm: int):
        return Table_Dimention(diameter_mm, diameter_mm, circular=True)
