import re
import networkx as nx
import matplotlib.pyplot as plt

def collapse_serial_nodes(g: nx.DiGraph,logged_nodes:list) -> nx.DiGraph:
    """Combine unlogged nodes in sequences.

    Example:
        A -> B -> C -> D
        If only A and D are logged, then the sequence is collapsed as:
        A -> B,C -> D

    Arguments:
        g: Call graph
        logged_nodes (list): Nodes not to combine in sequences.

    Returns:
        Modified graph.
    """
    for node in g:
        # Ensure that the node is unlogged (logged subroutines are not changed)
        if node not in logged_nodes:
            out_edges = g.out_edges(node)
            # Ensure that there is a single outward node (i.e. a sequence).
            if len(out_edges) == 1:
                for n in out_edges:
                    next_node = n[1]
                # Collapse if the two nodes are not logged.
                if next_node not in logged_nodes:
                    g = nx.contracted_nodes(g,node,next_node,self_loops=False)
                    g = nx.relabel_nodes(g, {node: f"{node},{next_node}"})
    return g

def collapse_all_serial_nodes(g: nx.DiGraph, logged_nodes: list) -> nx.DiGraph:
    """Apply `collapse_serial_nodes` until all serial nodes in a graph are
    combined.
    
    Args:
        g: Directed call graph.
        logged_nodes: List of nodes that produce a log.
    
    Return:
        Modified directed call graph."""
    while True:
        n1 = g.number_of_nodes()
        g = collapse_serial_nodes(g, logged_nodes)
        if n1 == g.number_of_nodes():
            g = group_collapsed_nodes(g)
            break
    return g

def collapse_parallel_nodes(g: nx.DiGraph,logged_nodes:list) -> nx.DiGraph:
    """Combine unlogged nodes in parallel.

    Example:
        A -> B -> D and A -> C -> D
        If only A and D are logged, then the sequence is collapsed as:
        A -> B|C -> D

    Arguments:
        g: Call graph
        logged_nodes (list): Nodes not to combine in sequences.

    Returns:
        Modified graph.
    """
    for node in g:
        # Ensure that the node is unlogged (logged subroutines are not changed)
        if node not in logged_nodes:
            out_edges = g.out_edges(node)
            destinations = []
            for edge in out_edges:
                destinations.append(edge[1])
            in_edges = g.in_edges(node)
            sources = []
            for edge in in_edges:
                sources.append(edge[0])
            # `candidates` are possible parallel nodes.
            candidate_edges = []
            for s in sources:
                candidate_edges += g.out_edges(s)
            candidates = []
            for edge in candidate_edges:
                if not edge[1] in logged_nodes and edge[1] != node:
                    candidates.append(edge[1])
            # Check if one candidate is parallel to node.
            for candidate in candidates:
                edges = g.out_edges(candidate)
                candidate_destinations = []
                for edge in edges:
                    candidate_destinations.append(edge[1])
                edges = g.in_edges(candidate)
                candidate_sources = []
                for edge in edges:
                    candidate_sources.append(edge[0])
                if (sorted(sources) == sorted(candidate_sources) and
                        sorted(destinations)==sorted(candidate_destinations)):
                    g = nx.relabel_nodes(g, {node: f"{node}|{candidate}"})
                    g.remove_node(candidate)
    return g

def collapse_all_parallel_nodes(g: nx.DiGraph,logged_nodes:list) -> nx.DiGraph:
    """Apply `collapse_parallel_nodes` until all parallel nodes in a graph are
    combined.
    
    Args:
        g: Directed call graph.
        logged_nodes: List of nodes that produce a log.
    
    Return:
        Modified directed call graph."""
    while True:
        n1 = g.number_of_nodes()
        g = collapse_parallel_nodes(g, logged_nodes)
        if n1 == g.number_of_nodes():
            g = group_collapsed_nodes(g)
            break
    return g

def group_collapsed_nodes(g: nx.DiGraph) -> nx.DiGraph:
    """Add parenthesis around newly collapsed nodes.
    
    Example:
        A -> B,C,D -> D
        A -> (B,C,D) -> D
    
    Args:
        g: Directed call graph.
    
    Returns:
        Modified call graph.
    """
    for node in g:
        # If the node contains characters "," or "|" and it is not placed
        # between parenthesis, it means that it was newly created.
        if ((("," in node) or ("|" in node)) and
                node[0] != "(" and node[-1] != ")"):
            g = nx.relabel_nodes(g, {node: f"({node})"})
    return g

def make_directed_graph(edge_filename: str="edges.txt", separator: str="->"
        ) -> nx.DiGraph:
    """Read a file of edges to make a directed call graph. The file needs to
    be formatted as:
    <subroutine 1 Name> <separator> <subroutine 2 Name>
    It can contain an arbitrary number of lines.
    
    Args:
        edge_filename: Name of the file that contains edges.
        separator: Character or sequence of characters that separate nodes.
    
    Returns:
        Directed graph as described by the file."""
    g = nx.DiGraph()
    # Obtain edges
    with open(edge_filename, "r") as edge_file:
        edges = edge_file.readlines()
        edges = [line.rstrip() for line in edges]
    # Include edges in graph.
    for edge in edges:
        raw_edges = re.split(separator, edge)
        stripped_edges = [e.strip() for e in raw_edges]
        g.add_edge(stripped_edges[0], stripped_edges[1])
    return g

def get_logged_nodes(log_filename: str="logged_nodes.txt") -> list:
    """Obtain the list of subroutines that produce a log.
    
    Args:
        log_filename: File path
    
    Returns:
        List of the elements contained in the file."""
    logged_nodes = []
    with open(log_filename, "r") as logged_nodes_file:
        logged_nodes = logged_nodes_file.readlines()
        logged_nodes = [line.rstrip() for line in logged_nodes]
    return logged_nodes

def get_source(g: nx.DiGraph) -> str:
    """Obtain the source node of the graph and stop the program if more than
    a single source is found.
    
    Args:
        g: Directed call graph.
    
    Returns:
        Source node."""
    sources = [node for node in g if g.in_degree(node) == 0]
    if len(sources) != 1:
        print(f"ERROR More than one source: {sources}")
        exit()
    return sources[0]

def process_graph(g: nx.DiGraph, logged_nodes: list) -> nx.DiGraph:
    """Simplify a call graph to combine nodeswhose execution cannot be
    accurately assessed from logs.
    
    Args:
        g: Directed call graph.
    
    Returns:
        Modified call graph."""
    while True:
        n_nodes = g.number_of_nodes()
        g = collapse_all_serial_nodes(g, logged_nodes)
        g = collapse_all_parallel_nodes(g, logged_nodes)
        if n_nodes == g.number_of_nodes():
            break
    return g

def view_graph(g: nx.DiGraph, logged_nodes: list) -> None:
    """Display the call graph with logged nodes in grey and unlogged nodes in
    white.
    
    Args:
        g: Directed call graph.
        logged_nodes: List of nodes that produce logs."""
    color_map = ['lightgrey' if node in logged_nodes else 'white' for node in g]
    nx.draw_networkx(g, node_color=color_map)
    plt.show()
