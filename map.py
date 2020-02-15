from graphviz import Digraph


class Map:
    def __init__(self, name, nodes=None):
        self.name = name
        self.nodes = set(nodes) if nodes else set()

    def add(self, node):
        self.nodes.add(node)

    def remove(self, node):
        self.nodes.remove(node)

    def __str__(self):
        d = Digraph(self.name, graph_attr={'concentrate': 'true'})
        for node in self.nodes:
            if node.connections:
                for connection in node.connections:
                    d.edge(node.name, connection.name)
            else:
                d.node(node.name)
        return str(d)


class Node:
    '''Representation of a node in '''

    def __init__(self, name, connections=None):
        self.name = name
        self.connections = set(connections) if connections else set()
        for node in self.connections:
            node.connections.add(self)

    # TODO: ADD *UP
    def connect(self, node):
        self.connections.add(node)
        node.connections.add(self)

    def disconnect(self, node):
        self.connections.remove(node)
        node.connections.remove(self)

    def __str__(self):
        d = Digraph()
        if self.connections:
            for node in self.connections:
                d.edge(self.name, node.name)
        else:
            d.node(self.name)
        return str(d)
