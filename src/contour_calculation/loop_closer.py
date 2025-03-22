
from __future__ import annotations
from matplotlib.path import Path
from typing import List
from src.contour_calculation.contour_loop import ContourLoop, ContourLoopBuilder
from src.spacial.table_dimention import Table_Dimention
from src.contour_calculation.linked_list import LinkedList, ListNode
from src.logger import get_logger
import logging

logger = get_logger("loop closer", logging.DEBUG)


class BorderPoint(ListNode):
    def __init__(self, border_position: float, frag_stop_node: BorderPoint, loop_frag_idx: int):
        super().__init__()
        self.border_position = border_position
        self.frag_stop_node = frag_stop_node
        self.loop_frag_idx = loop_frag_idx
    def is_start_end(self):
        return self.frag_stop_node is not None
    def is_stop_end(self):
        return self.frag_stop_node is None
    def get_stop_end(self):
        return self.frag_stop_node
    def smaller_than(self, other: BorderPoint):
        return self.border_position < other.border_position
    def __str__(self):
        return "BP({:0.2f}, {}, {})".format(self.border_position, "ptr" if self.frag_stop_node else "None", self.loop_frag_idx)


def merge_loop_fragments(paths: List[Path], table_dim: Table_Dimention) -> List[ContourLoop]:
    
    # Return this
    contour_loops: List[ContourLoop] = []
    
    border_points = LinkedList()
    
    # Enumerate Frags in List
    for i, path in enumerate(paths):
        # No processing needed for closed loops
        if path.codes[-1] == Path.CLOSEPOLY:
            if len(path.vertices) < 4:
                continue
            contour_loops.append(ContourLoop(path.vertices[:-1]))
            continue
        # Loop Fragments
        stop_node = BorderPoint(
            table_dim.get_border_position(path.vertices[-1]), None, i
        )
        border_points.append_right(stop_node)
        border_points.append_right(BorderPoint(
            table_dim.get_border_position(path.vertices[0]), stop_node, i
        ))
        
    # Sort list by border order
    border_points.sort()
    
    # Join Frags
    while border_points.get_size() > 0:
        contour_loop_builder = ContourLoopBuilder(table_dim)
        # Get the first stop point
        node_itr: BorderPoint = border_points.get_head()
        while not node_itr.is_stop_end():
            node_itr = node_itr.get_next()
        loop_start_node = node_itr
        # Connect Frags until the loop is closed
        while True:
            # Record this loop fragment
            contour_loop_builder.append_path_frag(paths[node_itr.loop_frag_idx])
            # Move to nest start end
            prev_node_itr = node_itr
            node_itr = node_itr.get_next()
            if node_itr is None:
                node_itr = border_points.get_head()
            border_points.remove_node(prev_node_itr)
            # Move to corrisponding stop end
            prev_node_itr = node_itr
            node_itr = node_itr.get_stop_end()
            border_points.remove_node(prev_node_itr)
            if node_itr is loop_start_node:
                break
        # Concatinate linked frags
        contour_loops.append(contour_loop_builder.get_contour_loop())

    return contour_loops


def merge_all_loop_fragments(all_paths: List[List[Path]], table_dim: Table_Dimention) -> List[List[ContourLoop]]:
    all_contours: List[List[ContourLoop]] = []
    for i, paths in enumerate(all_paths):
        merged_loop_fragments = merge_loop_fragments(paths, table_dim)
        if len(merged_loop_fragments) == 0:
            continue
        all_contours.append(merged_loop_fragments)
    return all_contours