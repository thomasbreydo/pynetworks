'''
nets-and-nodes
===============

A package that provides structure for networks of interconnected nodes, using
the DOT language for representation.'''

from graphviz import Digraph


class Network:
    '''Contain several interconnected ``Node`` objects.'''

    def __init__(self, name, nodes=None):
        self.name = name
        self.nodes = set(nodes) if nodes else set()

    def __str__(self):
        graph = Digraph(self.name, graph_attr={'concentrate': 'true'})
        for node in self.nodes:
            if node.connections:
                for connection in node.connections:
                    graph.edge(node.name, connection.name)
            else:
                graph.node(node.name)
        return str(graph)

    def add(self, node):
        '''Add ``node`` to this ``Network``.'''
        self.nodes.add(node)

    def remove(self, node):
        '''Remove ``node`` from this ``Network``.'''
        self.nodes.remove(node)


class Node:
    '''Hold a graph theory node its connections.'''

    def __init__(self, name, connections=None):
        self.name = name
        self.connections = set(connections) if connections else set()
        for node in self.connections:
            node.connections.add(self)

    def __str__(self):
        graph = Digraph()
        if self.connections:
            for node in self.connections:
                graph.edge(self.name, node.name)
        else:
            graph.node(self.name)
        return str(graph)

    def connect(self, other):
        '''Add a connection between this ``Node`` and ``other``.'''
        self.connections.add(other)
        other.connections.add(self)

    def disconnect(self, other):
        '''Remove the connection between this ``Node`` and ``other``.'''
        self.connections.remove(other)
        other.connections.remove(self)
