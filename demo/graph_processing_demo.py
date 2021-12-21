"""Graph simplification demonstration.

The script creates a graph whose node represent subroutines. Subroutines that
produce a log at runtime are labelled in grey. Unlogged subroutines are not
labelled. The algorithm combines unlogged nodes to simplify the graph."""

# Change working directory to file location and enable relative imports.
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
import sys
sys.path.insert(0, "../path_reconstructor")

import networkx as nx
import graph_processing as gp

G = nx.DiGraph([
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D'),
    ('D', 'F'),
    ('F', 'G'),
    ('G', 'H'),
    ('H', 'I'),
    ('H', 'K'),
    ('K', 'J'),
    ('I', 'J')
])
logged_nodes = ['A', 'F', 'J']

gp.view_graph(G, logged_nodes)
G = gp.process_graph(G, logged_nodes)
gp.view_graph(G, logged_nodes)
