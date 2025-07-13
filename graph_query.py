import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

# Load CSV file
file_path = 'parsed_relations_output.csv'
df = pd.read_csv(file_path)

# Build MultiDiGraph
G = nx.MultiDiGraph()
for _, row in df.iterrows():
    source = row['id']
    for i in range(1, 9):
        rel = row.get(f'relation_{i}')
        if pd.notna(rel):
            parts = rel.split()
            if len(parts) == 2:
                relation, target = parts
                G.add_edge(source, int(target), relation=relation)

# DiGraph for safe visualization
G_simple = nx.DiGraph()
for u, v, data in G.edges(data=True):
    if not G_simple.has_edge(u, v):
        G_simple.add_edge(u, v, relation=data['relation'])

# Helper functions
def get_parents(node):
    return [u for u, v, d in G.in_edges(node, data=True) if d['relation'] == 'childof']

def get_children(node):
    return [v for u, v, d in G.out_edges(node, data=True) if d['relation'] == 'childof']

def get_grandparents(node):
    return [gp for parent in get_parents(node) for gp in get_parents(parent)]

def get_grandchildren(node):
    return [gc for child in get_children(node) for gc in get_children(child)]

def get_peers(node):
    peers = set()
    for u, v, d in G.edges(data=True):
        if d['relation'] == 'peerof':
            if u == node:
                peers.add(v)
            elif v == node:
                peers.add(u)
    return list(peers)

def get_can_precede(node):
    return [v for u, v, d in G.out_edges(node, data=True) if d['relation'] == 'canprecede']

def get_can_follow(node):
    return [u for u, v, d in G.in_edges(node, data=True) if d['relation'] == 'canprecede']

def get_ancestors(node):
    return list(nx.ancestors(G_simple, node))

def get_descendants(node):
    return list(nx.descendants(G_simple, node))

def get_roots():
    return [n for n in G.nodes if G.in_degree(n) == 0]

def get_leaves():
    return [n for n in G.nodes if G.out_degree(n) == 0]

# Streamlit GUI
st.title("📊 CAPEC ID Analysis")

node = st.number_input("Enter Node ID to Explore", min_value=0, step=1)

if st.button("🔍 Analyze Node"):
    parents = get_parents(node)
    grandparents = get_grandparents(node)
    children = get_children(node)
    grandchildren = get_grandchildren(node)
    peers = get_peers(node)
    can_precede = get_can_precede(node)
    can_follow = get_can_follow(node)
    ancestors = get_ancestors(node)
    descendants = get_descendants(node)
    roots = get_roots()
    leaves = get_leaves()

    st.subheader("📌 Related Nodes for ID: {}".format(node))
    st.write("**Parents:**", parents)
    st.write("**Grandparents:**", grandparents)
    st.write("**Children:**", children)
    st.write("**Grandchildren:**", grandchildren)
    st.write("**Peers:**", peers)
    st.write("**Can Precede:**", can_precede)
    st.write("**Can Follow:**", can_follow)
    st.write("**Ancestors:**", ancestors)
    st.write("**Descendants:**", descendants)
    st.write("**Is Root?:**", node in roots)
    st.write("**Is Leaf?:**", node in leaves)

    st.subheader("🖼 Visualize Related Nodes")
    sub_nodes = set([node] + parents + grandparents + children + grandchildren + peers + can_precede + can_follow + ancestors + descendants)
    subG = G_simple.subgraph(sub_nodes)
    pos = nx.spring_layout(subG, seed=42)
    plt.figure(figsize=(12, 9))
    nx.draw(subG, pos, with_labels=True, node_color='lightblue', node_size=700, font_size=10)
    edge_labels = nx.get_edge_attributes(subG, 'relation')
    nx.draw_networkx_edge_labels(subG, pos, edge_labels=edge_labels, font_size=8)
    st.pyplot(plt)

st.markdown("---")
st.write("This tool provides deep graph analysis and visual context for CAPEC nodes based on their relationships.")
st.markdown("---")
st.markdown("**👩‍💻 Created by:** Bama, Sophie, and Sangeetha")

