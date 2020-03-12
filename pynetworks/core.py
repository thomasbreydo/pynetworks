

class Network:
    '''Contain several `Connection` objects in a named list.'''

    def __init__(self, connections=None, single_nodes=None, name=None):
        self.connections = list(connections) if connections else []
        for con in self.connections:
            con.node1.connect(con.node2, con.weight)
            con.node2.connect(con.node1, con.weight)
        self.single_nodes = list(single_nodes) if single_nodes else []
        self.name = str(name) if name else ''

    def __str__(self):
        return graph()

    def from_dot(self, dot):
        # TODO: USE REG EXP to find and interpret a--b[label=label]
        pass


class Connection:
    '''Represent an optionally weighted connection between two nodes.'''

    def __init__(self, node1, node2, weight=None):
        self.node1 = node1
        self.node2 = node2
        self.nodes = {node1, node2}
        self.weight = weight

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.node1!r}, {self.node2!r}'
                f'{f", {self.weight!r}" if self.weight else ""})')

    def __str__(self):
        return f'graph {{\n\t{self.edge()}\n}}'

    def __eq__(self, other):
        return self.nodes == other.nodes and self.weight == other.weight

    def edge(self):
        '''Return DOT language representation of this Connection.'''
        unlabeled = f'{self.node1.name} -- {self.node2.name}'
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled


class Node:
    def __init__(self, name, connections=None):
        self.name = name
        self.connections = list(connections) if connections else []

    def __str__(self):
        if self.connections:
            edges = "\n\t".join([con.edge() for con in self.connections])
            return f'graph {{\n\t{edges}\n}}'
        return f'graph {{\n\t{self.name}\n}}'

    def connect(self, other, weight=None):
        '''Add `Connection` between `self and `other` with weight weight`.'''
        self.connections.append(Connection(self, other, weight))
        other.connections.append(Connection(other, self, weight))

    def disconnect(self, other, weight=None):
        self.connections.remove(Connection(self, other, weight))
        other.connections.remove(Connection(other, self, weight))


def dot(single_nodes=[], connections=[], name=''):
    nodes = '\n\t'.join(single_nodes) + '\n'
    edges = '\n\t'.join([con.edge() for con in connections]) + '\n'
    return f'graph{f" {name} " if name else " "}{{{nodes}{edges}}}'
