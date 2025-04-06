
from src.topography_tree.topography_tree_node import TopographyTreeNode
from typing import List
from src.contour_calculation.contour_loop import ContourLoop, get_border_contour_loop
from shapely.geometry import Polygon
from src.spacial.table_dimention import Table_Dimention
from src.logger import get_logger
import logging
logger = get_logger("topo tree", logging.DEBUG)

SQ_MM_TO_SQ_CM = 100

# For a loop to be included in the tree, it must me at least this many mm squared in area
CRITICAL_LOOP_AREA = 20


def is_contour_loop_convex(loop: ContourLoop) -> bool:
    
    vertices = loop.get_vertices()
    
    # Calculate the signed area using the shoelace formula
    signed_area = 0
    
    # The loop needs to consider consecutive pairs of points
    # and wrap around to the first point
    for i in range(len(vertices)):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % len(vertices)]
        
        # Add the cross product
        signed_area += (x2 - x1) * (y2 + y1)
    
    # If the signed area is negative, the polygon is clockwise
    return signed_area > 0


def build_topography_tree(loop_layers: List[List[ContourLoop]], table_dim: Table_Dimention) -> TopographyTreeNode:
    
    topo_tree = TopographyTreeNode(get_border_contour_loop(table_dim))
    
    leaf_nodes = [topo_tree]
    
    too_small_loop_count = 0
    
    for loop_layer in loop_layers:
        
        if len(leaf_nodes) == 0:
            logger.error("No current leaf nodes. Skipping further tree generation")
            break
        
        new_leaf_nodes = []
        
        # Add each loop onto a tree
        for loop in loop_layer:
            
            if loop.get_area() < CRITICAL_LOOP_AREA:
                too_small_loop_count += 1
                continue
            
            if not is_contour_loop_convex(loop):
                logger.warning("Concave loop of area {:.2f} cm-sq encountered. Concave topo features are not supported yet. Skipping".format(
                    loop.get_area() / SQ_MM_TO_SQ_CM
                ))
                continue
            
            # Check all leaf nodes to see which one to add this loop to
            for leaf in leaf_nodes:
                
                if not leaf.loop.contains(loop.get_sample_vertex()):
                    continue
                
                node = TopographyTreeNode(loop)
                leaf.add_child(node)
                new_leaf_nodes.append(node)
                break
            
            else:
                logger.warning(
                    "Could not fit loop of area {:.2f} cm-sq into any {} leaves of the tree".format(
                        loop.get_area() / SQ_MM_TO_SQ_CM, len(leaf_nodes)
                    )
                )
            
        if len(new_leaf_nodes) > 0:
            leaf_nodes = new_leaf_nodes
    
    if too_small_loop_count > 0:
        logger.debug("Skipped {} loops because they were too small".format(too_small_loop_count))
    
    logger.info("Finished building topo tree")
    
    return topo_tree
