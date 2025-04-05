
from src.spacial.table_dimention import Table_Dimention
from src.geography_to_gcode import convert_elevation_data_to_path
from src.visualization.visualize_contour import dump_contour_image
import numpy as np

# Note: This serves mainly as regrssion testing for the whole algorithm

def _generate_interesting_elevation_data(rows, cols):
    # Create grid for x and y
    # Create grid for x and y, equally spaced
    x = np.linspace(-5, 5, cols)
    y = np.linspace(-5, 5, rows)
    
    # Create meshgrid from the x and y grids
    X, Y = np.meshgrid(x, y)
    
    a = (2,2)
    b = (-2,-2)
    
    # Calculate the distance to the point (1, 1) for each cell
    distance_to_a = np.sqrt((X - a[0])**2 + (Y - a[1])**2)
    distance_to_b = np.sqrt(((X - b[0])**2) * 1.4 + (Y - b[1])**2)
    
    return np.maximum((np.max(distance_to_a) - distance_to_a), (np.max(distance_to_b) - distance_to_b) *  1.2)


def test_basic():
    
    table_dim = Table_Dimention(200, 100)
    elevation_data = _generate_interesting_elevation_data(table_dim.get_width_mm(), table_dim.get_height_mm())
    
    recv_path = convert_elevation_data_to_path(elevation_data, table_dim)
    
    assert len(recv_path) == 5731
    # Just test a few points stay the same for regression
    assert np.allclose(recv_path[1000], np.array([21.9742247, 63.31658291]))
    assert np.allclose(recv_path[3000], np.array([151.51515152,  17.63267845]))
    assert np.allclose(recv_path[5000], np.array([76.39282703, 13.5678392]))


def test_basic_closer_contours():
    
    table_dim = Table_Dimention(200, 100)
    elevation_data = _generate_interesting_elevation_data(table_dim.get_width_mm(), table_dim.get_height_mm())
    
    recv_path = convert_elevation_data_to_path(elevation_data, table_dim, num_contours=25)
    
    assert len(recv_path) == 7345
    # Just test a few points stay the same for regression
    assert np.allclose(recv_path[1000], np.array([75.53762393, 53.76884422]))
    assert np.allclose(recv_path[3000], np.array([121.80924486,  64.8241206]))
    assert np.allclose(recv_path[7000], np.array([0,  100]))
