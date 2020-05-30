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
        if not isinstance(other, Path):
            raise TypeError("'<' not supported between instances of"
                            f'{type(self).__name__!r}  and '
                            f'{type(other).__name__!r}')
        return self.weight < other.weight

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
def shortest_path(start, end, _tail_weight=0, _visited=None, _best_path=None):
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

    for edge in start.edges:
        if edge.node2 not in _visited:
            new_weight = edge.weight + _tail_weight
            try:
                keep_going = new_weight < _best_path.weight
            except AttributeError:  # catches _best_path is None
                # still no best --> we are forced to keep going
                path = shortest_path(
                    edge.node2, end,
                    _tail_weight=new_weight,
                    _visited=_visited | {start},
                )
                try:
                    _best_path = Path([edge]) + path
                except TypeError:  # no path found
                    pass
            else:
                if keep_going:
                    path = shortest_path(
                        edge.node2, end,
                        _tail_weight=new_weight,
                        _visited=_visited | {start},
                        _best_path=_best_path,
                    )
                    try:
                        _best_path = Path([edge]) + path
                    except TypeError:  # no path found
                        pass

    return _best_path


@memoize
def shortest_path_through_network(start, network, _tail_weight=0,
                                  _visited=None, _best_path=None):
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
    new_path_was_found = False
    edges_were_skipped = False

    for edge in start.edges:
        if edge.node2 not in _visited:
            new_weight = edge.weight + _tail_weight
            try:
                skip_this_edge = new_weight >= _best_path.weight
            except AttributeError:  # catches _best_path is None
                # still no best --> we MUST to keep going
                pass
            else:
                if skip_this_edge:
                    edges_were_skipped = True
                    continue
            path = shortest_path_through_network(
                edge.node2, reduced_set,
                _tail_weight=new_weight,
                _visited=_visited | {start},
                _best_path=_best_path,
            )
            try:
                _best_path = Path([edge]) + path
            except TypeError:  # no path found
                pass
            else:
                new_path_was_found = True

    if new_path_was_found:
        return _best_path
    if edges_were_skipped:
        raise _IncompleteSearch('search was not exhaustive.')
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
