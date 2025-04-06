
from src.topography_tree.build_topography_tree import is_contour_loop_convex
from src.contour_calculation.contour_loop import ContourLoop


def test_convex_loop():
    # Verticies going clockwise
    vertices = [(0, 0), (0, 1), (1, 1), (1, 0)]
    
    loop = ContourLoop(vertices)
    
    is_convex = is_contour_loop_convex(loop)
    
    assert is_convex == True
    
    
def test_concave_loop():
    # Verticies going counter-clockwise
    vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
    
    loop = ContourLoop(vertices)
    
    is_convex = is_contour_loop_convex(loop)
    
    assert is_convex == False
    