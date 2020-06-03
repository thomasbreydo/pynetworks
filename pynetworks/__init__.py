'''pynetworks
==========

A Python package that provides structure for networks of interconnected
nodes using the DOT language for representation.
'''

from .networks import Edge
from .networks import Network
from .networks import Node
from .networks import generate_network
from .dot import dotgraph
from .dot import escape_dot_id
from .pathfinding import Path
from .pathfinding import memoize
from .pathfinding import path_exists
from .pathfinding import shortest_path
from .pathfinding import shortest_path_through_network


__version__ = "0.5.4"

__all__ = ['Edge',
           'Network',
           'Node',
           'generate_network',
           'dotgraph',
           'escape_dot_id',
           'Path',
           'memoize',
           'path_exists',
           'shortest_path',
           'shortest_path_through_network'
           ]
