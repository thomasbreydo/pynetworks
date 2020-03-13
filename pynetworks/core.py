class Network:
    '''Contain a network of interconnected `Node` objects.'''

    def __init__(self, all_nodes=None, name=None):
        self.all_nodes = set(all_nodes) if all_nodes else set()
        self.name = str(name) if name else ''
        self.update()  # set self.isolated_nodes and self.connections

    def __str__(self):
        return dotgraph(self.isolated_nodes, self.connections, self.name)

    def update(self):
        '''Update `self.connections` and `self.isolated_nodes`.'''
        self.isolated_nodes = set()
        self.connections = []
        seen = set()  # store reverses of seen connections
        for node in self.all_nodes:
            if node.connections:
                for con in node.connections:
                    if con.reverse() in seen:
                        continue  # opposite connection
                    else:
                        self.connections.append(con)
                        seen.add(con)
            else:
                self.isolated_nodes.add(node)

    def from_dotgraph(self, dotgraph):
        '''TODO: USE REG EXP to find and interpret a -- b [label=2].'''
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

    def __hash__(self):
        return hash(self.node1) ^ hash(self.node2) ^ hash(self.weight)

    def __eq__(self, other):
        return (self.node1, self.node2, self.weight) == (other.node1,
                                                         other.node2,
                                                         other.weight)

    def reverse(self):
        return Connection(self.node2, self.node1, self.weight)

    def edge(self):
        '''Return DOT language representation of this Connection.'''
        unlabeled = f'{self.node1.name} -- {self.node2.name}'
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled


class Node:
    '''Contain a named node, with weighted connections.

    `connected_to` is a list of tuples of the form `(node, weight)`
    >>> Node('My Node', [(my_node1, 5), (my_node2, 4)])
    '''

    def __init__(self, name):
        self.name = name
        self.connections = []

    def __str__(self):
        if self.connections:
            return dotgraph(connections=self.connections)
        return dotgraph(isolated_nodes=[self])

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return id(self) == id(other)

    def connect(self, other, weight=None):
        '''Add `Connection` between `self` and `other` with `weight`.'''
        self.connections.append(Connection(self, other, weight))
        other.connections.append(Connection(other, self, weight))

    def disconnect(self, other, weight=None):
        '''Remove `Connection` between `self` and `other` with `weight`.'''
        self.connections.remove(Connection(self, other, weight))
        other.connections.remove(Connection(other, self, weight))

    def isolate(self):
        '''Remove all connections from `self.connections`.'''
        self.connections = []


def dotgraph(isolated_nodes=[], connections=[], name=''):
    '''DOT representation of undirected graph with inputted properties.'''
    nodes = '\n\t'.join([str(node.name) for node in isolated_nodes])
    middle = '\n\t' if isolated_nodes and connections else ''
    edges = '\n\t'.join([con.edge() for con in connections])
    return (f'graph {f"{name} " if name else ""}'
            f'{{\n\t{nodes}{middle}{edges}\n}}')
