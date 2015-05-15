'''
created  10/06/2014

by sperez

makes hive panel from user input
'''

import sys
import os
import argparse
import networkx as nx
import numpy as np
import string
from gexf import read_gexf
from ntpath import basename, dirname
from uttilities_panel import *
from file_skeletons import parameters_file, html_file, methods_file

NODE_MEASURES = [nx.degree_centrality,
                nx.clustering,
                nx.betweenness_centrality, 
                nx.closeness_centrality,
                component_membership,
                ]

EDGE_MEASURES = [nx.edge_betweenness_centrality]

NUM_AXES = 3


def get_all_attributes(G):
    '''iters through nodes and edges to get their attributes'''
    nodeKeys = []
    edgeKeys = []
    
    for n in G.nodes():
        nodeKeys.extend(G.node[n].keys())
    nodeKeys = set(nodeKeys)

    for s,t in G.edges():
        edgeKeys.extend(G[s][t].keys())
    edgeKeys = set(edgeKeys)

    return list(nodeKeys), list(edgeKeys)

def make_js_files(G):
    '''make a network in js format'''
    nodeAttributes = G.graph['nodeAttributes'] #names of attributes
    edgeAttributes = G.graph['edgeAttributes']
    graphName = G.graph['title']

    newnodeFile = os.path.join(G.graph['folder'],"{0}_nodes.js".format(graphName))
    newedgeFile = os.path.join(G.graph['folder'],"{0}_edges.js".format(graphName))

    f = open(newnodeFile, 'w')
    f.write('var SVGTitle = "{0} Hive Panel"\n'.format(graphName.replace('_',' ')))
    f.write('var nodes = [\n')
    for node in G.nodes():
        line = '    {name: \'' + str(node) +'\''
        for attribute in nodeAttributes:
            line  += ', '+attribute+': \'' + str(G.node[node][attribute]) + '\''
        line += '},\n'
        f.write(line)
    f.write('];')
    f.close()

    f = open(newedgeFile,'w')
    f.write('var links = [\n')
    for (s,t) in G.edges():
        line = '  {source: nodes['+str(s)+'], target: nodes['+str(t)+']'
        for attribute in edgeAttributes:
            line  += ', '+attribute+': \'' + str(G.edge[s][t][attribute]) + '\''
        line += '},\n'
        f.write(line)
    f.write('];')
    f.close()
    return None

def make_panel_parameters_file(G):
    fileName = os.path.join(G.graph['folder'],"{0}_parameters.js".format(G.graph['title']))
    f = open(fileName, 'w')
    newfile = parameters_file.format(G.graph['axes'],
                    G.graph['double'],
                    '"'+G.graph['nodeAttributes'][0]+'"',
                    '"'+G.graph['nodeAttributes'][1]+'"',
                    '"'+G.graph['nodeAttributes'][0]+'":"linear"',
                    '"'+G.graph['nodeAttributes'][1]+'":"linear"',
                    )
    f.write(newfile)
    f.close()
    return None

def make_html_file(G):
    fileName = os.path.join(G.graph['folder'],"{0}_panel.html".format(G.graph['title']))
    f = open(fileName, 'w')
    newfile = html_file.format()
    f.write(newfile)
    f.close()
    return None

def make_panel_methods(G):
    fileName = os.path.join(G.graph['folder'],"panel_methods.js")
    f = open(fileName, 'w')
    newfile = methods_file.format()
    f.write(newfile)
    f.close()
    return None

def make_panel(G):
    make_js_files(G)
    make_panel_parameters_file(G)
    make_html_file(G)
    make_panel_methods(G)
    return None

def main(*argv):
    '''handles user input and creates a panel'''
    parser = argparse.ArgumentParser(description='This scripts takes networks and created the necessary file to make an interactive Hive panel')
    parser.add_argument('-input', help='Location of network file')
    parser.add_argument('-format', help='Input format of network')
    parser.add_argument('-nodes', help='Location of node network file')
    parser.add_argument('-edges', help='Location of edge network file')
    parser.add_argument('-title', help='Title/Name of graph')
    parser.add_argument('-folder', help='Output folder')
    parser.add_argument('-axes', help='Number of axes',default=NUM_AXES)
    parser.add_argument('-double', help='Makes hive plots with doubled axes', action = 'store_true')
    args = parser.parse_args()

    #Get graph in networkx format
    if args.format=='graphml':
        print "Reading .graphml as a networkx graph."
        G = import_graphml(args.input)
        title = basename(args.input).split('.')[0]
        folder = dirname(args.input)
    elif args.format=='gexf':
        #need a specific version of networkx for read_gexf to work
        # import pkg_resources
        # pkg_resources.require("networkx==1.7")
        # print "Reading .gefx as a networkx graph."
        # G = import_gexf(args.input)
        print "Gexf files currently not supported."
        sys.exit()
    elif args.format=='txt':
        print "Reading .txt as a networkx graph."
        G = import_graph(args.nodes, args.edges)
        title = basename(args.nodes).split('.')[0]
        folder = dirname(args.nodes)
    else:
        print "Please specify the format of your network: .gexf, .graphml, or a 2 .txt files with node and edge attribute."
        parser.print_help()
        sys.exit()


    if args.title:
        title = args.title

    if args.folder:
        folder = args.folder

    #store all the plotting info in the graph as attributes
    G.graph['axes']=args.axes
    G.graph['double']=args.double
    G.graph['folder']=folder
    G.graph['title']=title
    G.graph['nodeAttributes'],G.graph['edgeAttributes']=get_all_attributes(G)
    for m in NODE_MEASURES:
        G.graph['nodeAttributes'].append(m.__name__)
        measures = m(G)
        nx.set_node_attributes(G,m.__name__,measures)

    for m in EDGE_MEASURES:
        G.graph['edgeAttributes'].append(m.__name__)
        measures = m(G)
        nx.set_edge_attributes(G,m.__name__,measures)

    for n,v in G.graph.iteritems():
        print n,v

    print 'Making panel.'
    make_panel(G,)



if __name__ == "__main__":
    main(*sys.argv[1:])

# file = "C:\\Users\\Sarah\\Dropbox\\1-Hive panels\\Diseasome\\diseasome.gexf"
# f = open(file,'r')
# print f.readlines()
# convert_gexf(file)






