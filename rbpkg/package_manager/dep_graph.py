from __future__ import unicode_literals

from itertools import chain

import six


class Vertex(object):
    """A vertex in the dependency graph.

    Each vertex contains an item and edges to other vertices.
    """

    def __init__(self, item):
        """Initialize a vertex.

        Args:
            item (object):
                The item stored in the vertex.
        """
        self.item = item
        self.out_neighbors = []


class DependencyGraph(object):
    """Manages a graph of dependencies.

    The graph provides for items to depend on other items, and for a resulting
    order of dependencies to be returned (through :py:meth:`iter_sorted`).

    Items that form circular dependencies are allowed, and will not generate
    an error.
    """

    def __init__(self, items={}):
        """Initialize the graph.

        Args:
            items (dict, optional):
                A dictionary of items to lists of dependencies.
        """
        self._vertices = []
        self._vertex_cache = {}

        for item, dependencies in six.iteritems(items):
            self.add(item, dependencies)

    def add(self, item, dependencies=[]):
        """Add an item and its dependencies to the graph.

        Args:
            item (object):
                The item being added to the graph.

            dependencies (list, optional):
                A list of other items that this depends on.
        """
        vertex = self._add_vertex(item)

        for dep in dependencies:
            vertex.out_neighbors.append(self._add_vertex(dep))

    def iter_sorted(self):
        """Iterate through all items in sorted dependency order.

        Yields:
            object:
            Each item in the graph, in dependency order.
        """
        visited_vertices = set()

        return chain.from_iterable(
            self._toposort(vertex, visited_vertices)
            for vertex in self._vertices
            if vertex not in visited_vertices
        )

    def __contains__(self, item):
        return item in self._vertex_cache

    def _toposort(self, vertex, visited_vertices):
        """Perform a topological sort of the graph, starting at a vertex.

        This will recursively traverse through all unvisited edges, starting
        at this vertex, and yield all results.

        Args:
            vertex (Vertex):
                The starting vertex of the topological sort.

            visited_vertices (set):
                The set of vertices that have been visited. This will be
                updated with new vertices.

        Yields:
            object:
            Each reachable unvisited item in the graph, in dependency order,
            starting at this vertex.
        """
        visited_vertices.add(vertex)

        for neighbor in vertex.out_neighbors:
            if neighbor not in visited_vertices:
                for i in self._toposort(neighbor, visited_vertices):
                    yield i

        yield vertex.item

    def _add_vertex(self, item):
        """Add a vertex for an item.

        If the item already exists in the graph, the existing vertex will
        be returned.

        Args:
            item (object):
                The item to add.

        Returns:
            Vertex:
            The vertex for the item.
        """
        try:
            return self._vertex_cache[item]
        except KeyError:
            vertex = Vertex(item)
            self._vertices.append(vertex)
            self._vertex_cache[item] = vertex

            return vertex
