
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import euclidean

def get_total_length(path: npt.NDArray[np.float64]) -> float:
    """
    Returns the total path length
    """
    total_dist_mm = 0
    for i in range(len(path) - 1):
        total_dist_mm += euclidean(path[i], path[i+1])
    return total_dist_mm
