import inspect
import functools
from .dot import dotgraph


class Path(list):
    '''Store :class:`Edge` objects connecting two :class:`Node`
    objects.

    Parameters
    ----------
    edges : iterable, optional
        All :class:`Edge` objects in this :class:`Path`. If left
        out, the path is initialized empty.

    Attributes
    ----------
    edges
    '''

    def __str__(self):
        return dotgraph(edges=self)

    def __add__(self, other):
        return Path(super().__add__(other))

    def __repr__(self):
        return object.__repr__(self)

    def __lt__(self, other):
        if isinstance(other, Path):
            return self.weight < other.weight
        return NotImplemented

    @property
    def weight(self):
        '''Sum of the weights of all of the :class:`Edge`
        objects in this :class:`Path`.

        :type: numerical
        '''
        return sum(edge.weight for edge in self)


class _IncompleteSearch(Exception):
    pass


def memoize(shortest_path_func):
    '''Cache a path-finding function that expects two input parameters.

    The path-finding function may additionally accept some number of
    private parameters that don't affect cache.

    Examples
    --------
    Accessing cache.

    >>> shortest_path.cache  # see note for supported functions
    {...}


    Clearing cache.

    >>> shortest_path.cache_clear()  # see note for supported functions
    >>> shortest_path.cache
    {}

    Note
    ----
    Supported path-finding functions:

    - :meth:`shortest_path`
    - :meth:`shortest_path_through_network`
    - :meth:`path_exists`
    '''
    memo = {}
    all_params = iter(inspect.signature(shortest_path_func).parameters)
    param1_name = next(all_params)
    param2_name = next(all_params)

    @functools.wraps(shortest_path_func)
    def memoized_shortest_path_func(*args, **kwargs):
        try:
            param1 = args[0]
        except IndexError:  # both cacheable params passed as kwargs
            param1 = kwargs[param1_name]
            param2 = kwargs[param2_name]
        else:
            try:
                param2 = args[1]
            except IndexError:  # second cacheable param passed as kwarg
                param2 = kwargs[param2_name]

        cachekey = tuple(frozenset(param) if isinstance(param, set)
                         else param for param in [param1, param2])

        try:
            return memo[cachekey]
        except KeyError:
            try:
                path = shortest_path_func(*args, **kwargs)
            except _IncompleteSearch:
                return None  # but don't cache
            else:
                memo[cachekey] = path
                return path

    memoized_shortest_path_func.cache_clear = memo.clear
    memoized_shortest_path_func.cache = memo
    # pylint: disable=no-member
    memoized_shortest_path_func.__doc__ += '''
    Note
    ----
    This function is cached by the :meth:`memoize` function.
    '''
    return memoized_shortest_path_func


@memoize
def shortest_path(start, end, _visited=None,
                  _tail_weight=None,  # weight from the start of the best path
                  _best_path_weight=None):
    '''Find the shortest path between ``start`` and ``end``.

    Parameters
    ----------
    start: :class:`Node`
    end: :class:`Node`

    Returns
    -------
    :class:`Path` ``None``
        If a path exists from ``start`` to ``end``, return that
        :class:`Path` object. Otherwise, return ``None``.
    '''
    if start is end:
        return Path()
    if _visited is None:
        _visited = set()
    edges_were_skipped = False

    for edge in start.edges:
        if edge.node2 not in _visited:
            try:
                new_tail_weight = edge.weight + _tail_weight
            except TypeError:  # catches _tail_weight is None
                # haven't found a best --> we MUST keep going
                new_tail_weight = None  # still no tail
            else:
                # move on if weight of a path down this edge will exceed best
                if new_tail_weight >= _best_path_weight:
                    edges_were_skipped = True
                    continue
            path = shortest_path(
                edge.node2, end,
                _visited=_visited | {start},
                _tail_weight=new_tail_weight,
                _best_path_weight=_best_path_weight,
            )
            try:
                best_path = Path([edge]) + path
            except TypeError:  # no path found
                pass
            else:
                _best_path_weight = best_path.weight
                # ensure future calls will keep track of tail:
                _tail_weight = 0  # change it from None to 0
    try:
        return best_path
    except NameError:  # never found a path
        if edges_were_skipped:
            # the exception gets handled by memoize() wrapper, returning None
            # but NOT caching result (a path may exist!)
            raise _IncompleteSearch('although a path may exist, some searches '
                                    'aborted because the weight exceeded the '
                                    'current best.')
        return None


@memoize
def shortest_path_through_network(start, network, _visited=None,
                                  # weight from the start of the best path
                                  _tail_weight=None,
                                  _best_path_weight=None):
    '''Find the shortest path from ``start`` through all other
    :class:`Node` objects in ``network``.

    Parameters
    ----------
    start : :class:`Node`
        Start of the returned :class:`Path`.
    network : :class:`Network`
        Fully-connected network through which the returned
        :class:`Path` travels.

    Returns
    -------
    :class:`Path` ``None``
        If a path exists from ``start`` to ``end``, return that
        :class:`Path` object. Otherwise, return ``None``.
    '''
    try:
        reduced_set = network.all_nodes - {start}
    except AttributeError:  # network is set of Node, not Network
        reduced_set = network - {start}
    if not reduced_set:
        return Path()
    if _visited is None:
        _visited = set()
    edges_were_skipped = False

    for edge in start.edges:
        if edge.node2 not in _visited:
            try:
                new_tail_weight = edge.weight + _tail_weight
            except TypeError:  # catches _tail_weight is None
                # haven't found a best --> we MUST keep going
                new_tail_weight = None  # still no tail
            else:
                # move on if weight of a path down this edge will exceed best
                if new_tail_weight >= _best_path_weight:
                    edges_were_skipped = True
                    continue
            path = shortest_path_through_network(
                edge.node2, reduced_set,
                _visited=_visited | {start},
                _tail_weight=new_tail_weight,
                _best_path_weight=_best_path_weight,
            )
            try:
                best_path = Path([edge]) + path
            except TypeError:  # no path found
                pass
            else:
                _best_path_weight = best_path.weight
                # ensure future calls will keep track of tail:
                _tail_weight = 0  # change it from None to 0

    try:
        return best_path
    except NameError:  # never found a path
        if edges_were_skipped:
            # the exception gets handled by memoize() wrapper, returning None
            # but NOT caching result (a path may exist!)
            raise _IncompleteSearch('although a path may exist, some searches '
                                    'aborted because the weight exceeded the '
                                    'current best.')
        return None


@memoize
def path_exists(start, end, _visited=None):
    '''Check if a path exists between ``start`` and ``end``.

    Parameters
    ----------
    start : :class:`Node`
    end : :class:`Node`

    Returns
    -------
    bool
        ``True`` if a path exists, otherwise ``False``.
    '''

    if start == end:
        return True
    if _visited is None:
        _visited = set()

    for edge in start.edges:
        if edge.node2 not in _visited:
            if path_exists(edge.node2, end, _visited=_visited | {start}):
                return True
    return False
