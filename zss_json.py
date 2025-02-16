import json
from zss import Node, simple_distance
import unittest
import time

def json_to_tree(json_obj):
    """Convert a JSON object to a tree."""
    stack = []
    root = None
    
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            root = Node(key)
            stack.append((root, value))
            break  # Ensure only one root
    
    while stack:
        parent, children = stack.pop()
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    for k, v in child.items():
                        child_node = Node(k)
                        parent.addkid(child_node)
                        stack.append((child_node, v))
                else:
                    parent.addkid(Node(child))
        elif isinstance(children, dict):
            for k, v in children.items():
                child_node = Node(k)
                parent.addkid(child_node)
                stack.append((child_node, v))
        else:
            parent.addkid(Node(children))
    
    return root


def count_nodes(node):
    """Count the number of nodes in the tree."""
    if node is None:
        return 0
    return 1 + sum(count_nodes(child) for child in node.children)


def print_tree(node, level=0):
    """Print the tree."""
    if node is not None:
        print("    " * level + f"- {node.label}")
        for child in node.children:
            print_tree(child, level + 1)


def tree_error_rate(ref_tree, hyp_tree):
    """Calculate the tree error rate between two trees."""
    return simple_distance(ref_tree, hyp_tree) / count_nodes(ref_tree)


if __name__ == "__main__":
    unittest.main()