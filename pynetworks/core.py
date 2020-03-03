class Network:
    '''Contain several ``Connection`` objects in a named list.'''

    def __init__(self, connections=None, name=None):
        self.connections = list(connections) if connections else []
        self.name = str(name) if name else ''

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{f"{self.connections!r}" if self.connections else ""}'
                f'{f", {self.name!r}" if self.name else ""})')

    def __str__(self):
        links = "\n\t".join([con.graph() for con in self.connections])
        return f'graph{f" {self.name} " if self.name else " "}{{\n\t{links}\n}}'

    def from_dot(self, dot):
        # TODO: USE REG EXP to find and interpret a--b[label=label]
        pass


class Connection:
    '''Contain an optionally weighted connection between two nodes.'''

    def __init__(self, node1, node2, weight=None):
        self.node1 = node1
        self.node2 = node2
        self.nodes = {node1, node2}
        self.weight = weight

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.node1!r}, {self.node2!r}'
                f'{f", {self.weight!r}" if self.weight else ""})')

    def __str__(self):
        return f'graph {{\n\t{self.graph()}\n}}'

    def __eq__(self, other):
        return self.nodes == other.nodes and self.weight == other.weight

    def graph(self):
        '''Return DOT language representation of this connection.'''
        unlabeled = f'{self.node1} -- {self.node2}'
        if self.weight:
            return unlabeled + f' [label={self.weight}]'
        return unlabeled
