
from src.geography.topography_tree.topography_tree_node import TopographyTreeNode
from typing import List
from src.geography.contour_calculation.contour_loop import ContourLoop, get_border_contour_loop
from shapely.geometry import Polygon
from src.utils import Table_Dimention


def build_topography_tree(loop_layers: List[List[ContourLoop]], table_dim: Table_Dimention) -> TopographyTreeNode:
    
    topo_tree = TopographyTreeNode(get_border_contour_loop(table_dim))
    
    # make a tree root for each loop in the first layers
    for loop in loop_layers[0]:
        topo_tree.add_child(TopographyTreeNode(loop))
        
    leaf_nodes = topo_tree.children
    
    for loop_layer in loop_layers[1:]:
        
        new_leaf_nodes = []
        
        # Add each loop onto a tree
        for loop in loop_layer:
            
            # Check all leaf nodes to see which one to add this loop to
            for leaf in leaf_nodes:
                
                if not leaf.loop.contains(loop.get_sample_vertex()):
                    continue
                
                node = TopographyTreeNode(loop)
                leaf.add_child(node)
                new_leaf_nodes.append(node)
                break
            
            else:
                raise Exception("loop did not fit in tree")
            
        leaf_nodes = new_leaf_nodes
        
    return topo_tree
