
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import euclidean
from src.spacial.table_dimention import Table_Dimention

def rotate_points(points: npt.NDArray[np.float64], table_dim: Table_Dimention, rotation_degrees: int) -> npt.NDArray[np.float64]:
    """
    Rotate a list of 2D points around the center of the width x height rectangle.
    
    Args:
        points: List of [x, y] points to rotate
        table_dim: Table diemntions before rotating
        rotation_degrees: Rotation angle in degrees (0, 90, 180, or 270)
        
    Returns:
        List of rotated [x, y] points
    """
    # Convert points to numpy array for easier manipulation
    points_array = np.array(points)
    
    # Center of the rectangle
    center_x = table_dim.get_width_mm() / 2
    center_y = table_dim.get_height_mm() / 2
    
    # Translate points to origin (center of the rectangle)
    centered_points = points_array - np.array([center_x, center_y])
    
    # No need for complex rotation matrices since we only have 90° increments
    rotated_points = []
    
    if rotation_degrees == 0:
        # No rotation
        rotated_points = centered_points
    elif rotation_degrees == 90:
        # 90° clockwise rotation: (x, y) -> (-y, x)
        rotated_points = np.column_stack((-centered_points[:, 1], centered_points[:, 0]))
    elif rotation_degrees == 180:
        # 180° rotation: (x, y) -> (-x, -y)
        rotated_points = -centered_points
    elif rotation_degrees == 270:
        # 270° clockwise rotation: (x, y) -> (y, -x)
        rotated_points = np.column_stack((centered_points[:, 1], -centered_points[:, 0]))
    else:
        raise ValueError("Rotation must be 0, 90, 180, or 270 degrees")
    
    # Handle width/height swap for 90° and 270° rotations
    if rotation_degrees in [90, 270]:
        # Swap width and height for the translation back
        center_x, center_y = center_y, center_x
    
    # Translate back from origin
    final_points = rotated_points + np.array([center_x, center_y])
    
    return final_points


def get_total_length(path: npt.NDArray[np.float64]) -> float:
    """
    Returns the total path length
    """
    total_dist_mm = 0
    for i in range(len(path) - 1):
        total_dist_mm += euclidean(path[i], path[i+1])
    return total_dist_mm
