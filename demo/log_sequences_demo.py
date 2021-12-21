"""Exection path reconstruction demonstration.

The script uses a directed call graph and a list of logs to reconstruct
the execution path of a program and report precision and accuracy."""

# Change working directory to file location and enable relative imports.
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
import sys
sys.path.insert(0, "../path_reconstructor")

import re
import networkx as nx
import log_sequences

G = nx.DiGraph([
    ('A', 'B'),
    ('B', 'G'),
    ('G', 'E'),
    ('E', 'E'),
    ('A', 'C'),
    ('C', 'E'),
    ('A', 'D'),
    ('D', 'F'),
    ('F', 'D')
])
real = "A,C,E,C,B,G,E,C,E,E,E,E,B,C,B,C,E,C,E,C,C,C,C,C,B,G,E"
logs = "E,B,E,E,E,E,E,B,B,E,E,B,E"
log_nodes = re.split(r',', logs)
real_nodes = re.split(r',', real)

reconstructed = log_sequences.reconstruct_path(G, log_nodes, 'A')
matched = log_sequences.match_reconstruction(real_nodes, reconstructed)
print(f"Real execution path:          {real_nodes}")
print(f"Reconstructed execution path: {reconstructed}")
print(f"Matched execution path:       {matched}")
print(f"Precision: {log_sequences.evaluate_precision(real_nodes,reconstructed)}")
print(f"Recall: {log_sequences.evaluate_recall(real_nodes, matched)}")
