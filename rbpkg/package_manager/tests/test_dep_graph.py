from __future__ import unicode_literals

from rbpkg.package_manager.dep_graph import DependencyGraph
from rbpkg.testing.testcases import TestCase


class DependencyGraphTests(TestCase):
    """Unit tests for rbpkg.package_manager.dep_graph.DependencyGraph."""

    def test_iter_sorted_simple(self):
        """Testing DependencyGraph.iter_sorted in simple case"""
        graph = DependencyGraph()
        graph.add(3, [2])
        graph.add(2, [1])
        graph.add(1, [])

        self.assertEqual(list(graph.iter_sorted()), [1, 2, 3])

    def test_iter_sorted_complex(self):
        """Testing DependencyGraph.iter_sorted with complex dependencies"""
        graph = DependencyGraph()
        graph.add(5, [9])
        graph.add(12, [9, 6, 15])
        graph.add(15, [9, 2])
        graph.add(9, [14, 20])
        graph.add(6, [14, 2])

        self.assertEqual(list(graph.iter_sorted()),
                         [14, 20, 9, 5, 2, 6, 15, 12])

    def test_iter_sorted_circular_ref(self):
        """Testing DependencyGraph.iter_sorted with circular reference"""
        graph = DependencyGraph()
        graph.add(1, [2])
        graph.add(2, [1])

        self.assertEqual(list(graph.iter_sorted()), [2, 1])
