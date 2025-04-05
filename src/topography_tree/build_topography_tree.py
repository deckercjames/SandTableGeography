
from src.topography_tree.topography_tree_node import TopographyTreeNode
from typing import List
from src.contour_calculation.contour_loop import ContourLoop, get_border_contour_loop
from shapely.geometry import Polygon
from src.spacial.table_dimention import Table_Dimention
from src.logger import get_logger
import logging
logger = get_logger("topo tree", logging.DEBUG)

# For a loop to be included in the tree, it must me at least this many mm squared in area
CRITICAL_LOOP_AREA = 10


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
                    "Could not fit loop of length {}, area {} into any {} leaves of the tree".format(
                        len(loop.get_vertices()), loop.get_area(), len(leaf_nodes)
                    )
                )
            
        if len(new_leaf_nodes) > 0:
            leaf_nodes = new_leaf_nodes
    
    if too_small_loop_count > 0:
        logger.debug("Skipped {} loops because they were too small".format(too_small_loop_count))
    
    logger.info("Finished building topo tree")
    
    return topo_tree
