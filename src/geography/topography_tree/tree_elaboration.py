import numpy as np
from scipy.spatial.distance import euclidean
import math
from src.geography.topography_tree.topography_tree_node import TopographyTreeNode
from src.table_dimention import Table_Dimention
from src.geography.contour_calculation.contour_loop import ContourLoop
from typing import List
import numpy as np
from scipy.spatial.distance import euclidean
import math
from src.logger import get_logger
import logging

logger = get_logger("elaborator", logging.DEBUG)


def find_best_transition(from_loop, to_loop, sample_size=50):
    """
    Find a good transition point between two loops using sampling and local refinement.
    
    Args:
        from_loop: List of [x, y] points representing the first loop
        to_loop: List of [x, y] points representing the second loop
        sample_size: Number of points to sample from from_loop
        
    Returns:
        Tuple of (from_idx, to_idx, score) representing the best transition points
    """
    # Convert loops to numpy arrays
    from_loop_np = np.array(from_loop)
    to_loop_np = np.array(to_loop)
    
    # Sample points from from_loop
    if sample_size >= len(from_loop):
        sample_indices = np.arange(len(from_loop))
    else:
        sample_indices = np.linspace(0, len(from_loop) - 1, sample_size, dtype=int)
    
    # Helper function to evaluate a from_idx against the to_loop
    def evaluate_from_point(from_idx):
        # Find best to_idx and score for this from_idx
        best_to_idx, best_score = find_best_to_point(from_loop_np, to_loop_np, from_idx)
        return from_idx, best_to_idx, best_score
    
    # Find the best from_idx in our sample
    best_from_idx = 0
    best_to_idx = 0
    best_score = float('-inf')
    
    for from_idx in sample_indices:
        from_idx, to_idx, score = evaluate_from_point(int(from_idx))
        if score > best_score:
            best_score = score
            best_from_idx = from_idx
            best_to_idx = to_idx
    
    # Perform local refinement using gradient descent
    max_iterations = 10
    current_from_idx = best_from_idx
    current_to_idx = best_to_idx
    current_score = best_score
    
    for _ in range(max_iterations):
        # Try neighbors
        left_idx = (current_from_idx - 1) % len(from_loop)
        right_idx = (current_from_idx + 1) % len(from_loop)
        
        # Evaluate neighbors
        left_from_idx, left_to_idx, left_score = evaluate_from_point(left_idx)
        right_from_idx, right_to_idx, right_score = evaluate_from_point(right_idx)
        
        # Find the best neighbor
        if left_score > current_score and left_score >= right_score:
            current_from_idx = left_idx
            current_to_idx = left_to_idx
            current_score = left_score
        elif right_score > current_score:
            current_from_idx = right_idx
            current_to_idx = right_to_idx
            current_score = right_score
        else:
            # No improvement, we've reached a local maximum
            break
    
    return (current_from_idx, current_to_idx)


def find_best_to_point(from_loop_np, to_loop_np, from_idx):
    """
    Helper function to find the best to_point for a given from_point.
    
    Args:
        from_loop_np: Numpy array of from_loop points
        to_loop_np: Numpy array of to_loop points
        from_idx: Index of the point in from_loop to evaluate
        
    Returns:
        Tuple of (best_to_idx, score)
    """
    # Get current point and calculate tangent
    current_point = from_loop_np[from_idx]
    next_idx = (from_idx + 1) % len(from_loop_np)
    next_point = from_loop_np[next_idx]
    
    # Calculate tangent direction
    tangent_vector = next_point - current_point
    tangent_length = np.linalg.norm(tangent_vector)
    
    # Skip if points are too close (tangent undefined)
    if tangent_length < 1e-6:
        # Fall back to distance-only evaluation for this point
        best_to_idx = 0
        best_dist = float('inf')
        
        for to_idx in range(len(to_loop_np)):
            dist = euclidean(current_point, to_loop_np[to_idx])
            if dist < best_dist:
                best_dist = dist
                best_to_idx = to_idx
                
        # Simple distance-based score
        max_possible_dist = 100  # Arbitrary constant for normalization
        score = 1 - min(1, best_dist / max_possible_dist)
        return best_to_idx, score
    
    # Normalize tangent vector
    tangent_vector = tangent_vector / tangent_length
    
    # Find the best match in to_loop
    best_to_idx = 0
    best_score = float('-inf')
    
    # Calculate max distance for normalization
    max_distance = 0
    for to_point in to_loop_np:
        dist = euclidean(current_point, to_point)
        max_distance = max(max_distance, dist)
    
    if max_distance == 0:
        max_distance = 1  # Avoid division by zero
    
    # Evaluate against all points in to_loop
    for to_idx in range(len(to_loop_np)):
        # Calculate distance score
        distance = euclidean(current_point, to_loop_np[to_idx])
        distance_score = 1 - (distance / max_distance)
        
        # Calculate angle score
        to_next_idx = (to_idx + 1) % len(to_loop_np)
        to_dir = to_loop_np[to_next_idx] - to_loop_np[to_idx]
        to_dir_length = np.linalg.norm(to_dir)
        
        if to_dir_length > 1e-6:
            to_dir = to_dir / to_dir_length
            dot_product = np.dot(tangent_vector, to_dir)
            dot_product = np.clip(dot_product, -1.0, 1.0)
            angle = math.acos(dot_product)
            angle_score = 1 - (angle / math.pi)
        else:
            angle_score = 0
        
        # Combine scores
        combined_score = 0.5 * distance_score + 0.5 * angle_score
        
        if combined_score > best_score:
            best_score = combined_score
            best_to_idx = to_idx
    
    return best_to_idx, best_score



def find_best_border_transition(table_dim: Table_Dimention, from_loop: ContourLoop, to_loop: ContourLoop) -> tuple[int, int]:
    
    best_dist = float('inf')
    best_pair = None
    
    # If we are transision between two loops, one is guarenteed to be within the other
    # Since they both touch the border, they must also both touch a border on the same side
    for i in from_loop.get_border_indices():
        for j in to_loop.get_border_indices():
            x0, y0 = from_loop.get_vertices()[i]
            x1, y1 = to_loop.get_vertices()[j]
            
            x_close = math.isclose(x0, x1)
            y_close = math.isclose(y0, y1)
            
            if x_close and y_close:
                return (i, j)
            
            dist = None
            
            if x_close:
                dist = abs(y0 - y1)
            elif y_close:
                dist = abs(x0 - x1)
                
            if dist is not None and dist < best_dist:
                best_dist = dist
                best_pair = (i, j)
                
    if best_pair is None:
        raise Exception("Could not find border link")
        
    return best_pair        


def find_shortest_transition(from_loop: ContourLoop, to_loop: ContourLoop) -> tuple[int, int]:
    # Convert loops to numpy arrays
    from_loop_np = np.array(from_loop.get_vertices())
    to_loop_np = np.array(to_loop.get_vertices())
    
    best_dist = float('inf')
    best_pair = None
    
    for i, from_pos in enumerate(from_loop_np):
        for j, to_pos in enumerate(to_loop_np):
            dist = euclidean(from_pos, to_pos)
            if dist >= best_dist:
                continue
            best_dist = dist
            best_pair = (i, j)
    return best_pair


def generate_tree_spiral_path(table_dim: Table_Dimention, root_node: TopographyTreeNode) -> List[tuple[float, float]]:
    
    path = []
    
    traversal_order = root_node.unravel_tree()
    
    logger.info("Unraveled tree of size {} into a traversal plan of length {}".format(root_node.get_size(), len(traversal_order)))
    
    next_enter_idx: int = None
    
    for i in range(len(traversal_order) - 1):
        
        curr_enter_idx = next_enter_idx
        
        current_contour_loop, must_complete = traversal_order[i]
        next_contour_loop, _ = traversal_order[i+1]
        
        
        # If they both touch the border, then get a total border traversal
        if current_contour_loop.touches_border() and next_contour_loop.touches_border():
            curr_exit_idx, next_enter_idx = find_best_border_transition(table_dim, current_contour_loop, next_contour_loop)
        elif not must_complete:
            curr_exit_idx, next_enter_idx = find_shortest_transition(current_contour_loop, next_contour_loop)
        else:
            curr_exit_idx, next_enter_idx = find_best_transition(current_contour_loop.get_vertices(), next_contour_loop.get_vertices())
        
        if curr_enter_idx is None:
            path.extend(np.roll(current_contour_loop.get_vertices(), -(curr_exit_idx+1), axis=0))
            continue
        
        if must_complete:
            path.extend(np.roll(current_contour_loop.get_vertices(), -(curr_enter_idx+1), axis=0))
        
        num_curr_vertices = len(current_contour_loop.get_vertices())
        circ_length = (curr_exit_idx - curr_enter_idx + num_curr_vertices) % num_curr_vertices
        path.extend(np.roll(current_contour_loop.get_vertices(), -(curr_enter_idx+1), axis=0)[:circ_length])

    return path
