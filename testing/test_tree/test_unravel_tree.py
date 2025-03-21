
from src.topography_tree.topography_tree_node import TopographyTreeNode

"""
Since the node data (loop) is not used. we can just use an integer
to track them and confirm order
"""

def test_unravel_one_level():
    root = TopographyTreeNode(0)
    root.add_child(TopographyTreeNode(1))
    root.add_child(TopographyTreeNode(2))
    recv_traversal = root.unravel_tree()
    exp_traversal = [
        (2, True),
        (0, False),
        (1, True),
        (0, True),
    ]
    assert recv_traversal == exp_traversal


def test_unravel_single_branch():
    root = TopographyTreeNode(0)
    child1 = TopographyTreeNode(1)
    root.add_child(child1)
    child2 = TopographyTreeNode(2)
    child1.add_child(child2)
    recv_traversal = root.unravel_tree()
    exp_traversal = [
        (2, True),
        (1, True),
        (0, True),
    ]
    assert recv_traversal == exp_traversal


def test_unravel_deepest_first():
    root = TopographyTreeNode(0)
    child1 = TopographyTreeNode(1)
    root.add_child(child1)
    child2 = TopographyTreeNode(2)
    child1.add_child(child2)
    child3 = TopographyTreeNode(3)
    child1.add_child(child3)
    child4 = TopographyTreeNode(4)
    child3.add_child(child4)
    recv_traversal = root.unravel_tree()
    exp_traversal = [
        (4, True),
        (3, True),
        (1, False),
        (2, True),
        (1, True),
        (0, True),
    ]
    assert recv_traversal == exp_traversal
