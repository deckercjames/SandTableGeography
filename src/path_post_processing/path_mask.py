
import numpy as np
import numpy.typing as npt
from src.spacial.table_dimention import Table_Dimention
from scipy.spatial.distance import euclidean
from typing import List
import logging
from src.logger import get_logger

logger = get_logger("path mask", logging.DEBUG)


def circle_line_intersection(circle_center, radius, line_start, line_end) -> List[npt.NDArray[np.float64]]:
    """
    Find the intersection points between a circle and a line segment.
    
    Parameters:
    - circle_center: tuple (x, y) representing the center of the circle
    - radius: radius of the circle
    - line_start: tuple (x1, y1) representing the start point of the line segment
    - line_end: tuple (x2, y2) representing the end point of the line segment
    
    Returns:
    - List of intersection points (could be empty, contain one point, or two points)
    """
    
    # Convert inputs to numpy arrays for easier vector operations
    center = np.array(circle_center, dtype=float)
    p1 = np.array(line_start, dtype=float)
    p2 = np.array(line_end, dtype=float)
    
    # Vector from p1 to p2
    d = p2 - p1
    
    # Length of the line segment
    line_length = np.linalg.norm(d)
    
    # If line segment length is zero, return empty list (no intersection with a point)
    if line_length == 0:
        return []
    
    # Normalize the direction vector
    d = d / line_length
    
    # Vector from center to line start
    f = p1 - center
    
    # Coefficients of the quadratic equation
    a = np.dot(d, d)  # This should be 1.0 since d is normalized
    b = 2 * np.dot(f, d)
    c = np.dot(f, f) - radius**2
    
    # Discriminant
    discriminant = b**2 - 4 * a * c
    
    # No intersection if discriminant is negative
    if discriminant < 0:
        return []
    
    # Calculate the two potential intersection points
    t1 = (-b + np.sqrt(discriminant)) / (2 * a)
    t2 = (-b - np.sqrt(discriminant)) / (2 * a)
    
    intersections = []
    
    # Check if t1 is within the line segment bounds [0, line_length]
    if 0 <= t1 <= line_length:
        intersections.append(tuple(p1 + t1 * d))
    
    # Check if t2 is within the line segment bounds [0, line_length]
    if 0 <= t2 <= line_length:
        # Avoid duplicates in case of tangent
        if not intersections or not np.allclose(p1 + t2 * d, intersections[0]):
            intersections.append(tuple(p1 + t2 * d))
    
    return intersections


def circular_arc_path(circle_center, radius, point1, point2, segment_length=1):
    """
    Creates a path of linear segments along the circumference of a circle,
    going clockwise from point1 to point2.
    
    Parameters:
    - circle_center: tuple (x, y) representing the center of the circle
    - radius: radius of the circle
    - point1: tuple (x1, y1) representing the starting point on the circle
    - point2: tuple (x2, y2) representing the ending point on the circle
    - segment_length: approximate length of each segment (optional)
    
    Returns:
    - List of points [(x1, y1), (x2, y2), ...] forming the path
    """
    # Convert inputs to numpy arrays
    center = np.array(circle_center, dtype=float)
    p1 = np.array(point1, dtype=float)
    p2 = np.array(point2, dtype=float)
    
    # Verify points are on the circle
    dist1 = np.linalg.norm(p1 - center)
    dist2 = np.linalg.norm(p2 - center)
    
    if not np.isclose(dist1, radius, atol=1e-10) or not np.isclose(dist2, radius, atol=1e-10):
        raise ValueError("Both points must be on the circle circumference")
    
    # Calculate angles of the two points
    v1 = p1 - center
    v2 = p2 - center
    
    theta1 = np.arctan2(v1[1], v1[0])
    theta2 = np.arctan2(v2[1], v2[0])
    
    # Ensure clockwise direction
    if theta1 < theta2:
        theta1 += 2 * np.pi
    
    # Total angle to cover (clockwise)
    angle_diff = theta1 - theta2
    if angle_diff == 0:
        angle_diff = 2 * np.pi  # Full circle if points are the same
    
    # Calculate segments based on desired segment length
    segment_arc_length = angle_diff * radius
    num_segments = max(2, int(np.ceil(segment_arc_length / segment_length)))
    
    # Create points along the arc
    path = [tuple(p1)]
    angle_step = angle_diff / num_segments
    
    for i in range(1, num_segments):
        angle = theta1 - i * angle_step
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        path.append((x, y))
    
    # Add the final point
    path.append(tuple(p2))
    
    return path


def _point_in_circle(circle_center, circle_radius, point) -> bool:
    return euclidean(circle_center, point) <= circle_radius


def crop_path_to_circle(path: npt.NDArray[np.float64], table_dim: Table_Dimention) -> npt.NDArray[np.float64]:
    
    logger.debug("Cropping path to circle...")
    
    circle_radius = table_dim.get_width_mm() / 2
    circle_center = np.array([circle_radius, circle_radius], dtype=float)
    
    currently_in_circle: bool = _point_in_circle(circle_center, circle_radius, path[0])
    last_intersection = None
    
    masked_path = []
    
    for i in range(1, len(path)):
        
        in_circle: bool = _point_in_circle(circle_center, circle_radius, path[i])
        
        if not currently_in_circle and not in_circle:
            continue
        
        if currently_in_circle and in_circle:
            masked_path.append(path[i])
            continue
        
        intersections = circle_line_intersection(circle_center, circle_radius, path[i-1], path[i])
        
        if len(intersections) != 1:
            logger.warning("Detected mask cross, but did not calculate one intersection. Got {}".format(intersections))
            continue
            
        intersection = intersections[0]
        
        # transitioning into the circle
        if in_circle and last_intersection is not None:
            masked_path.extend(circular_arc_path(circle_center, circle_radius, last_intersection, intersection))
        
        last_intersection = intersection
        currently_in_circle = in_circle
        
    logger.info("Path cropped to circle")
        
    return np.array(masked_path)