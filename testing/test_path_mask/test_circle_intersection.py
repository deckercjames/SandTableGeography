
from src.path_post_processing.path_mask import circle_line_intersection
import numpy as np


def test_two_intersections():
    circle_center = (0, 0)
    radius = 5
    line_start = (-10, 0)
    line_end = (10, 0)
    recv_intersections = circle_line_intersection(circle_center, radius, line_start, line_end)
    exp_intersections = [(5.0, 0.0), (-5.0, 0.0)]
    assert np.allclose(np.array(recv_intersections), np.array(exp_intersections))


def test_one_intersections():
    circle_center = (0, 0)
    radius = 5
    line_start = (0, 5)
    line_end = (10, 5)
    recv_intersections = circle_line_intersection(circle_center, radius, line_start, line_end)
    exp_intersections = [(0.0, 5.0)]
    assert np.allclose(np.array(recv_intersections), np.array(exp_intersections))


def test_zero_intersections():
    circle_center = (0, 0)
    radius = 5
    line_start = (0, 6)
    line_end = (10, 6)
    recv_intersections = circle_line_intersection(circle_center, radius, line_start, line_end)
    exp_intersections = []
    assert recv_intersections == exp_intersections
