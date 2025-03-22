
from __future__ import annotations
from abc import ABC

class ListNode(ABC):
    def __init__(self):
        self.next: ListNode = None
        self.prev: ListNode = None
    def smaller_than(self, other: ListNode):
        raise NotImplemented()
    def get_next(self) -> ListNode:
        return self.next
    

class LinkedList():
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    def append_right(self, node: ListNode) -> None:
        self.size += 1
        if self.head is None:
            self.head = node
            self.tail = node
            return
        self.tail.next = node
        node.prev = self.tail
        self.tail = node
    def get_head(self):
        return self.head
    def get_size(self):
        return self.size
    def sort(self):
        if self.head is None:
            return
        self.head = sort_linked_list(self.get_head())
        self.tail = self.head
        while self.tail.get_next() is not None:
            self.tail.next.prev = self.tail
            self.tail = self.tail.get_next()
    def remove_node(self, node_to_remove: ListNode):
        if not self.head:  # If the list is empty
            return

        if node_to_remove is self.head:  # Node to remove is the head
            self.head = self.head.next
            if self.head:  # If there's a node after the head, set its prev to None
                self.head.prev = None
        elif node_to_remove is self.tail:  # Node to remove is the tail
            self.tail = self.tail.prev
            if self.tail:  # If there's a node before the tail, set its next to None
                self.tail.next = None
        else:  # Node to remove is in the middle
            node_to_remove.prev.next = node_to_remove.next
            node_to_remove.next.prev = node_to_remove.prev
        self.size -= 1
    def __str__(self):
        node = self.head
        buf = "["
        while node is not None:
            # print(node)
            buf += str(node)
            node = node.get_next()
            if node is not None:
                buf += ", "
        buf += "]"
        return buf


def find_middle(head: ListNode) -> ListNode:
    """Find the middle node of the linked list using slow and fast pointers"""
    if head is None:
        return head
    
    slow = head
    fast = head
    
    # Fast pointer moves twice as fast as slow pointer
    # When fast reaches the end, slow will be at the middle
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
        
    return slow


def merge(left: ListNode, right: ListNode) -> ListNode:
    """Merge two sorted linked lists"""
    # Create a dummy head node
    dummy = ListNode()
    current = dummy
    
    # Compare nodes from both lists and merge them in sorted order
    while left and right:
        if left.smaller_than(right):
            current.next = left
            left = left.next
        else:
            current.next = right
            right = right.next
        current = current.next
    
    # Attach remaining nodes if any
    if left:
        current.next = left
    if right:
        current.next = right
        
    return dummy.next


def sort_linked_list(head: ListNode) -> ListNode:
    """
    Sort a linked list in ascending order using merge sort
    
    Args:
        head: The head node of the linked list
    
    Returns:
        The head node of the sorted linked list
    """
    # Base case
    if head is None or head.next is None:
        return head
    
    # Split the list into two halves
    mid = find_middle(head)
    second_half = mid.next
    mid.next = None  # Break the list into two parts
    
    # Recursively sort both halves
    left = sort_linked_list(head)
    right = sort_linked_list(second_half)
    
    # Merge the sorted halves
    return merge(left, right)
