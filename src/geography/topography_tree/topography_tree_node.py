
from __future__ import annotations
import numpy as np
import numpy.typing as npt
from typing import List
from src.geography.contour_calculation.contour_loop import ContourLoop
from collections import deque
import pickle

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
        
        
    def unravel_tree(self) -> List[tuple[ContourLoop, bool]]:
        tree_path = []
        if len(self.children) > 0:
            tree_path.extend(self.children[0].unravel_tree())
            for child in self.children[1:]:
                tree_path.append((self.loop, False))
                tree_path.extend(child.unravel_tree())
        tree_path.append((self.loop, True))
        return tree_path
            
        
    def pretty_print_tree(self, level=0):
        """Recursively prints the tree structure."""
        # Print the current node's level
        print('  ' * level + '|--' + str(self.loop))  # |-- is a visual marker for the branching

        # Recurse over each child and print with incremented indentation
        for child in self.children:
            child.pretty_print_tree(level + 1)
