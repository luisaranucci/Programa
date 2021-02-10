#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
import sys
import os.path

#run this file as "python convert_graphs.py file_in dir_out"

#getting the paths
in_path = sys.argv[1]
out_path = sys.argv[2]
out_path += in_path.split("/")[-1].split(".")[0] 
if os.path.exists(out_path):
    os.mkdir(out_path)

#reading input and creating empty graphs
graph = nx.read_graphml(in_path)
compound = nx.Graph()
reaction = nx.Graph()

#separating the types of nodes
types = nx.get_node_attributes(graph, "sbml type")
compound_nodes = [i for i in types.keys() if types[i] == "species"]
reaction_nodes = [i for i in types.keys() if types[i] == "reaction"]

#removing currency metabolites
currency = ['ATP ', 'ADP ', 'NADPH ', 'NADP+ ', 'NAD+ ', 'NADH ', 'Pi ', 'PPi ', 'CO2 ', 'H2O ', 'NH3 ', 'SO4(2-) ', 'H+ ', 'O2 ']    
first_names = nx.get_node_attributes(graph, "shared name")
remove_nodes = []

for i in first_names:
    if first_names[i][0:first_names[i].find("[")] in currency:
        compound_nodes.remove(i)
        remove_nodes.append(i)
        

compound.add_nodes_from(compound_nodes)
reaction.add_nodes_from(reaction_nodes)

#edges structure ([species_key, reaction_key, 0])
edges = nx.get_edge_attributes(graph, "interaction type")

#dict[reaction] = [reactants]
rr_list = [i for i in edges if edges[i] == "reaction-reactant"]
rr_dict = {}
for i in range(len(rr_list)):
    if rr_list[i][1] not in rr_dict.keys():
        rr_dict[rr_list[i][1]] = [rr_list[i][0]]
    else:
        rr_dict[rr_list[i][1]].append(rr_list[i][0])
        
#dict[reaction] = [products]
rp_list = [i for i in edges if edges[i] == "reaction-product"]
rp_dict = {}
for i in range(len(rp_list)):
    if rp_list[i][1] not in rp_dict.keys():
        rp_dict[rp_list[i][1]] = [rp_list[i][0]]
    else:
        rp_dict[rp_list[i][1]].append(rp_list[i][0])

#dict[compound] = [reactions]
compound_dict = {}
for i in edges:
    if i[0] not in compound_dict.keys():
        compound_dict[i[0]] = [i[1]]
    else:
        compound_dict[i[0]].append(i[1])

#make compound graph
for i in reaction_nodes:
    if i in rp_dict and i in rr_dict:
        for reactant in rr_dict[i]:
            for product in rp_dict[i]:
                compound.add_edge(reactant, product)

#make reaction graph
for i in compound_nodes:
    for r1 in compound_dict[i]:
        for r2 in compound_dict[i]:
            if r1 != r2 and not reaction.has_edge(r1, r2):
                reaction.add_edge(r1, r2)
                

#removing currency metabolites
compound.remove_nodes_from(remove_nodes)

#setting node attributes
compound_attr = {i:first_names[i] for i in first_names if i in compound_nodes}
reaction_attr = {i:first_names[i] for i in first_names if i in reaction_nodes}

nx.set_node_attributes(compound, compound_attr, "name")
nx.set_node_attributes(reaction, reaction_attr, "name")

#writing files
nx.write_gml(compound, out_path + "_compound.gml")
nx.write_gml(reaction, out_path + "_reaction.gml")





