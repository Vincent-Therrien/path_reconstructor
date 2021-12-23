import networkx as nx
import random

from itertools import islice
def k_shortest_paths(G, source, target, k=7, weight=None):
    try:
        return list(
            islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))
    except:
        return [[]]

def cut_executed_nodes(g: nx.DiGraph, path: list) -> list:
    """Remove the part of an execution path that was already executed.
    
    Example:
        Given
        - a call graph g: A -> B, B -> D, A -> C, C -> D
        - a log sequence: D, B
        The the actual sequence is (D, A, B), but the nodes are connected in
        the following sequence: (D, B|C, A, B). This function returns (D, B).
    
    Args:
        g: Directed call graph
        path: A list of nodes executed in sequence
    
    Returns:
        Shortened execution path.
    """
    for index, node in enumerate(path):
        shortened_paths = k_shortest_paths(g, node, path[-1])
        if len(shortened_paths) > 10:
            shortened_paths = shortened_paths[0:10]
        if shortened_paths:
            return path[index:]
    print("No ancestor node.")
    print(path)
    exit()

def is_path_direct(g: nx.DiGraph, path: list) -> bool:
    """Check if the path is possible or contains illogical sequences.
    
    Example:
        Given a call graph A -> B -> C, the sequence (C, B, A) is not
        possible because it is inconsistent with the call order.
    
    Args:
        g: Directed call graph.
        path: Node sequence.
    
    Returns:
        A boolean value indicating if the path is possible (True) or not
        (False)."""
    dir_change_index = 0
    for index, node in enumerate(path[:-1]):
        edges = g.in_edges(node)
        sources = []
        for e in edges:
            sources.append(e[1])
        next_node = path[index+1]
        if not (next_node in sources):
            dir_change_index = index
    for index, node in enumerate(path[dir_change_index:-1]):
        edges = g.out_edges(node)
        destinations = []
        for e in edges:
            destinations.append(e[1])
        next_node = path[index+1]
        if not (next_node in destinations):
            return []
    return path[dir_change_index:]

def find_execution_path(g: nx.DiGraph, u: nx.DiGraph,
        node1: str, node2: str, last_dif_node: str,
        logged_nodes: str) -> list:
    """Return a possible execution path between two nodes.
    
    The function first lists all possible paths that connect two nodes and
    then eliminates paths based on the following criteria:
    - Presence of logged nodes (apart from initial and terminal nodes).
    - Presence of reversed subroutine calls.
    If two paths are possible, one is selected randomly.
    
    Args:
        g: Directed graph
        u: Undirected graph, which must be a deepcopy of g.
        node1: Initial subroutine.
        node2: Terminal subroutine.
        last_dif_node: Previous node that is different from the node1.
    
    Returns:
        A possible execution path."""
    # Case 0: Recursive call of a subroutine to itself.
    if node1 == node2:
        edges = g.out_edges(node1)
        for e in edges:
            if e[1] == node2:
                return [node1, node2]
        node1 = last_dif_node
    # Case 1: Direct link between the two nodes.
    is_direct = True
    paths = k_shortest_paths(g, node1, node2)
    if len(paths) > 10:
        paths = paths[0:10]
    # Case 2: No direct link, must go back in the tree.
    if not paths:
        is_direct = False
        paths = k_shortest_paths(u, node1, node2)
        for p in paths:
            short_path = is_path_direct(g, p)
            if short_path:
                paths.append(short_path)
    # Remove paths with logged nodes because they are not possible.
    cleaned_paths = []
    for path in paths:
        if not (set(path[1:-1]) & logged_nodes):
            cleaned_paths.append(path)
    # Select a possible path.
    if not cleaned_paths:
        return []
    if is_direct:
        return random.choice(cleaned_paths)
    else:
        return cut_executed_nodes(g, random.choice(cleaned_paths))

def find_last_dif(nodes: list, new_node: str) -> str:
    """Find the last differing node.
    
    Args:
        nodes: List of reconstructed function calls.
        new_node: Next node to use for path reconstruction.
    
    Returns:
        Last subroutine that differs from `new_node`."""
    for i in reversed(nodes):
        if i != new_node:
            return i
    return new_node

def reconstruct_path(g: nx.DiGraph, logs: list, source: str) -> list:
    """Reconstruct an execution path from a call graph and logs.
    
    Args:
        g: Directed graph whose nodes correspond to function.
        logs: List of nodes that correspond to logs produced at runtime in
            order. The names must match elements in `g`.
        source: Source of `g`, that is, the program entry point.
    
    Returns:
        Reconstructed execution path as a list of nodes."""
    u = g.to_undirected()
    logged_nodes = set(logs)
    reconstruction = [source]
    last_dif_node = source
    for node in logs[0:]:
        last_dif_node = find_last_dif(reconstruction, node)
        new_path = find_execution_path(
            g, u, reconstruction[-1], node, last_dif_node, logged_nodes)[1:]
        if new_path:
            reconstruction += new_path
        else:
            reconstruction += [node]
    return reconstruction[1:]

def match_reconstruction(real: list, reconstructed: list) -> list:
    """Match a reconstructed execution path to the real execution path by
    adding empty elements between nodes.
    
    Args:
        real: List of subroutine executions.
        reconstructed: List of reconstructed subroutine executions.
    
    Returns:
        Matched execution path."""
    matched = []
    r_index = 0
    for node in real:
        if r_index == len(reconstructed):
            matched.append(' ')
        elif node == reconstructed[r_index]:
            matched.append(node)
            r_index += 1
        else:
            matched.append(' ')
    return matched

def get_true_positive(real: list, matched: list) -> int:
    """Get the number of elements that correspond to a real subroutine call.
    
    Args:
        real: List of subroutine executions.
        matched: Matched execution path.
    
    Return:
        Number of accurate nodes."""
    count = 0
    for index, r in enumerate(real):
        if r == matched[index]:
            count += 1
    return count

def evaluate_precision(real: list, reconstructed: list) -> float:
    """Calculate the precision of a reconstructed path. The function
    implements the equation: precision = TP / (N reconstructed subroutines).
    
    Args:
        real: List of subroutine executions.
        reconstructed: List of reconstructed subroutine executions.
    
    Returns:
        Precision"""
    matched = match_reconstruction(real, reconstructed)
    return get_true_positive(real, matched) / len(reconstructed)

def evaluate_recall(real: list, matched: list) -> float:
    """Calculate the recall of a reconstructed path. The function
    implements the equation: recall = TP / (N real subroutines).
    
    Args:
        real: List of subroutine executions.
        reconstructed: List of reconstructed subroutine executions.
    
    Returns:
        Recall"""
    return get_true_positive(real, matched) / len(matched)
