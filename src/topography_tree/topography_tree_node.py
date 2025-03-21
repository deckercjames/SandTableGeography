
from __future__ import annotations
from typing import List
from src.contour_calculation.contour_loop import ContourLoop

class TopographyTreeNode:
    def __init__(self, loop: ContourLoop):
        self.loop = loop
        self.children: List[TopographyTreeNode] = []
    
    
    def get_loop(self) -> ContourLoop:
        return self.loop
    
    
    def add_child(self, child: TopographyTreeNode):
        self.children.append(child)
        
        
    def get_size(self):
        size = 1
        for child in self.children:
            size += child.get_size()
        return size
    
    
    def get_max_depth(self) -> int:
        max_depth = 0
        for child in self.children:
            max_depth = max(max_depth, child.get_max_depth())
        return max_depth + 1
    
        
    def unravel_tree(self) -> List[tuple[ContourLoop, bool]]:
        """
        Unravels the tree, in a modified post-and-in-order-traversal, adding the node data (loop)
        to the list. The boolean indicates if it was added as part of post-order traversal.
        (i.e. it is the last time the traversal hits it). The children of each node
        are sorted by the deepest branch from them
        """
        child_idx_order = [(child.get_max_depth(), i) for i, child in enumerate(self.children)]
        child_idx_order.sort()
        child_idx_order = child_idx_order[::-1]
        
        tree_path = []
        for i, (_, child_idx) in enumerate(child_idx_order):
            tree_path.extend(self.children[child_idx].unravel_tree())
            if i < (len(child_idx_order) - 1):
                tree_path.append((self.loop, False))
        tree_path.append((self.loop, True))
        return tree_path
            
        
    def pretty_print_tree(self, level=0):
        """Recursively prints the tree structure."""
        # Print the current node's level
        print('  ' * level + '|--' + str(self.loop))  # |-- is a visual marker for the branching

        # Recurse over each child and print with incremented indentation
        for child in self.children:
            child.pretty_print_tree(level + 1)
