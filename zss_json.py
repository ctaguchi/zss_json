import json
from zss import Node, simple_distance

# Local import
import ted_cer

try:
    from editdist import distance as strdist
except ImportError:
    try:
        from editdistance import eval as strdist
    except ImportError:
        def strdist(a, b):
            if a == b:
                return 0
            else:
                return 1


def json_to_tree(json_obj: dict) -> Node:
    """Convert a JSON object to a tree.
    
    Parameters
    ----------
    json_obj : dict
        The JSON object.
    
    Returns
    -------
    Node
        The root node of the tree.
    """
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


def count_nodes(node: Node) -> int:
    """Count the number of nodes in the tree.
    
    Parameters
    ----------
    node : Node
        The root node.

    Returns
    -------
    int
        The number of nodes in the tree.
    """
    if node is None:
        return 0
    return 1 + sum(count_nodes(child) for child in node.children)


def print_tree(node: Node, level: int =0) -> None:
    """Print the tree.
    
    Parameters
    ----------
    node : Node
        The root node.
    level : int
        The level of the node in the tree.

    Returns
    -------
    None
    """
    if node is not None:
        print("    " * level + f"- {node.label}")
        for child in node.children:
            print_tree(child, level + 1)


def tree_error_rate(ref_tree: Node,
                    hyp_tree: Node,
                    substring_bonus: bool = False,
                    get_label=Node.get_label,
                    label_dist=strdist,
                    return_operations: bool = False) -> float:
    """Calculate the tree error rate between two trees.
    
    Parameters
    ----------
    ref_tree : Node
        The reference tree.
    hyp_tree : Node
        The hypothesis tree.
    substring_bonus : bool
        Whether to give a bonus for substrings based on substring match.
        Substring match is calculated as 1 - CER.

    Returns
    -------
    float
        The tree error rate.
    """
    if substring_bonus:
        dist = ted_cer.distance_with_cer(ref_tree,
                                  hyp_tree,
                                  Node.get_children,
                                  insert_cost=lambda node: label_dist('', get_label(node)),
                                  remove_cost=lambda node: label_dist(get_label(node), ''),
                                  update_cost=lambda a, b: label_dist(get_label(a), get_label(b)),
                                  return_operations=return_operations
                                  )
        return dist / count_nodes(ref_tree)
    else:
        return simple_distance(ref_tree, hyp_tree) / count_nodes(ref_tree)


if __name__ == "__main__":
    """Example usage of the functions.
    
    The hypothesis contains the following errors:
    - The definition_spanish field is a list instead of a string.
    - The pronunciation field uses the wrong pronunciation.
    """

    ref = """{"dictionary": [{"headword": "rina",
"pronunciations": ["řina", "rina"],
"part_of_speech": "v.",
"definition_spanish": "ir, viajar.",
"definition_kichwa": "Shuk llaktamanta shukman purishpa, pawashpa imashinapash anchuriy.",
"example_sentence": "Ñukapa llaktamanta rini."},
{"headword": "ruku",
"pronunciations": ["řuku", "ruku"],
"part_of_speech": "adj.",
"definition_spanish": "viejo, anciano.",
"definition_kichwa": "Achka watayuk runa.",
"example_sentence": "Kanpa ruku yayaka ¿maypitak kawsan?"}]}"""
    hyp = """{"dictionary": [{"headword": "rina",
"pronunciations": ["rina", "rina"],
"part_of_speech": "v.",
"definition_spanish": ["ir", "viajar"],
"definition_kichwa": "Shuk llaktamanta shukman purishpa, pawashpa imashinapash anchuriy.",
"example_sentence": "Ñukapa llaktamanta rini."},
{"headword": "ruku",
"pronunciations": ["ruku", "ruku"],
"part_of_speech": "adj.",
"definition_spanish": ["viejo", "anciano"],
"definition_kichwa": "Achka watayuk runa.",
"example_sentence": "Kanpa ruku yayaka ¿maypitak kawsan?"}]}"""
    ref_tree = json_to_tree(json.loads(ref))
    hyp_tree = json_to_tree(json.loads(hyp))
    print("Tree error rate:", tree_error_rate(ref_tree, hyp_tree, substring_bonus=False))
    print("Tree error rate with CER:", tree_error_rate(ref_tree, hyp_tree, substring_bonus=True))