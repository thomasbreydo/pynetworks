class Network:
    '''Contain a network of interconnected `Node` objects.'''

    def __init__(self, nodes=None, name=None):
        self.nodes = set(nodes) if nodes else set()
        self.connections = list(connections) if connections else []
        self.all_nodes = self._reset_and_get_all_nodes()

        self.name = str(name) if name else ''

# for con in self.connections:
#             con.node1.connect(con.node2, con.weight)

    def __str__(self):
        return dotgraph(self.single_nodes, self.connections, self.name)

    def from_dotgraph(self, dotgraph):
        '''TODO: USE REG EXP to find and interpret a--b[label=label]'''
        pass


class Connection:
    '''Represent an optionally weighted connection between two nodes.'''

    def __init__(self, node1, node2, weight=None):
        self.node1 = node1
        self.node2 = node2
        self.weight = weight

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.node1!r}, {self.node2!r}'
                f'{f", {self.weight!r}" if self.weight else ""})')

    def __str__(self):
        return dotgraph(connections=[self])

    def __eq__(self, other):
        return (self.node1, self.node2, self.weight == (other.node1, other.node2, other.weight)

    def edge(self):
        '''Return DOT language representation of this Connection.'''
        unlabeled=f'{self.node1.name} -- {self.node2.name}'
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled


class Node:
    def __init__(self, name, connections=None):
        self.name=name
        self.connections=list(connections) if connections else []

    def __str__(self):
        if self.connections:
            return dotgraph(connections=self.connections)
        return dotgraph(single_nodes=[self])

    def connect(self, other, weight=None):
        '''Add `Connection` between `self and `other` with weight `weight`.'''
        self.connections.append(Connection(self, other, weight))
        other.connections.append(Connection(other, self, weight))

    def disconnect(self, other, weight=None):
        self.connections.remove(Connection(self, other, weight))
        other.connections.remove(Connection(other, self, weight))

    def clear_connections(self):
        self.connections=[]


def dotgraph(single_nodes=[], connections=[], name=''):
    '''Return undirected graph'''
    nodes='\n\t'.join([str(node.name) for node in single_nodes])
    middle='\n\t' if single_nodes and connections else ''
    edges='\n\t'.join([con.edge() for con in connections])
    return (f'graph {f"{name} " if name else ""}'
            f'{{\n\t{nodes}{middle}{edges}\n}}')
