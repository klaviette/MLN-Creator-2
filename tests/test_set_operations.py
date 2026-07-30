"""
Tests for the inter-layer set-operation logic (AND / OR / NOT).

The pure functions (_parse_net_file and the set arithmetic) are reproduced
here directly, since they are embedded in the Tkinter GUI (tkinter/main.py)
and cannot be imported without starting a Tk event loop.
"""
import os
import sys
import unittest
import tempfile


# ── Helpers mirroring tkinter/main.py logic ───────────────────────────────────

def _parse_net_file(filepath):
    """Return (layer_name, node_list, edge_set) from a .net file."""
    with open(filepath, encoding='utf-8') as fh:
        lines = fh.readlines()
    layer_name = lines[0].strip()
    num_nodes  = int(lines[1].strip())
    nodes = [lines[i].strip() for i in range(3, 3 + num_nodes)]
    edges = set()
    for i in range(3 + num_nodes, len(lines)):
        raw = lines[i].strip()
        if not raw:
            continue
        parts = raw.split(',')
        if len(parts) >= 2:
            edges.add((parts[0].strip(), parts[1].strip()))
    return layer_name, nodes, edges


def _write_net_file(path, name, nodes, edges):
    """Write a minimal .net file matching the format produced by the engine."""
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(name + '\n')
        fh.write(str(len(nodes)) + '\n')
        fh.write(str(len(edges)) + '\n')
        for n in nodes:
            fh.write(n + '\n')
        for a, b in edges:
            fh.write(f'{a},{b},1.0000 \n')


def _run_set_op(net_files, op):
    """Apply AND / OR / NOT over a list of parsed .net files."""
    parsed = [_parse_net_file(fp) for fp in net_files]
    edge_sets = [p[2] for p in parsed]

    if op == 'AND':
        result = edge_sets[0].copy()
        for es in edge_sets[1:]:
            result &= es
    elif op == 'OR':
        result = set()
        for es in edge_sets:
            result |= es
    else:  # NOT
        result = edge_sets[0] - edge_sets[1]
    return result


# ── Test fixtures ─────────────────────────────────────────────────────────────

NODES = ['A', 'B', 'C', 'D']


class TestParseNetFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.net', delete=False, encoding='utf-8'
        )
        self.tmp.write('layer_x\n3\n2\nA\nB\nC\nA,B,1.0000 \nB,C,1.0000 \n')
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_layer_name_parsed(self):
        name, _, _ = _parse_net_file(self.tmp.name)
        self.assertEqual(name, 'layer_x')

    def test_node_list_parsed(self):
        _, nodes, _ = _parse_net_file(self.tmp.name)
        self.assertEqual(nodes, ['A', 'B', 'C'])

    def test_edges_parsed(self):
        _, _, edges = _parse_net_file(self.tmp.name)
        self.assertIn(('A', 'B'), edges)
        self.assertIn(('B', 'C'), edges)

    def test_edge_count(self):
        _, _, edges = _parse_net_file(self.tmp.name)
        self.assertEqual(len(edges), 2)

    def test_empty_lines_ignored(self):
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.net', delete=False, encoding='utf-8'
        ) as f:
            f.write('empty_test\n2\n1\nX\nY\n\nX,Y,1.0000 \n\n')
            path = f.name
        try:
            _, _, edges = _parse_net_file(path)
            self.assertEqual(edges, {('X', 'Y')})
        finally:
            os.unlink(path)


class TestAndOperation(unittest.TestCase):
    def _net(self, d, name, edges):
        path = os.path.join(d, name + '.net')
        _write_net_file(path, name, NODES, edges)
        return path

    def test_common_edge_kept(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B'), ('B', 'C')})
            p2 = self._net(d, 'l2', {('A', 'B'), ('C', 'D')})
            result = _run_set_op([p1, p2], 'AND')
            self.assertEqual(result, {('A', 'B')})

    def test_no_common_edges_empty(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B')})
            p2 = self._net(d, 'l2', {('C', 'D')})
            result = _run_set_op([p1, p2], 'AND')
            self.assertEqual(result, set())

    def test_identical_layers_unchanged(self):
        edges = {('A', 'B'), ('B', 'C')}
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', edges)
            p2 = self._net(d, 'l2', edges)
            result = _run_set_op([p1, p2], 'AND')
            self.assertEqual(result, edges)

    def test_three_layers_intersection(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B'), ('B', 'C'), ('C', 'D')})
            p2 = self._net(d, 'l2', {('A', 'B'), ('B', 'C')})
            p3 = self._net(d, 'l3', {('A', 'B'), ('C', 'D')})
            result = _run_set_op([p1, p2, p3], 'AND')
            self.assertEqual(result, {('A', 'B')})


class TestOrOperation(unittest.TestCase):
    def _net(self, d, name, edges):
        path = os.path.join(d, name + '.net')
        _write_net_file(path, name, NODES, edges)
        return path

    def test_union_of_disjoint_edges(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B')})
            p2 = self._net(d, 'l2', {('C', 'D')})
            result = _run_set_op([p1, p2], 'OR')
            self.assertEqual(result, {('A', 'B'), ('C', 'D')})

    def test_no_duplicates_on_shared_edge(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B')})
            p2 = self._net(d, 'l2', {('A', 'B')})
            result = _run_set_op([p1, p2], 'OR')
            self.assertEqual(len(result), 1)

    def test_union_superset_of_both_inputs(self):
        e1 = {('A', 'B'), ('B', 'C')}
        e2 = {('C', 'D'), ('A', 'B')}
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', e1)
            p2 = self._net(d, 'l2', e2)
            result = _run_set_op([p1, p2], 'OR')
            self.assertTrue(e1.issubset(result))
            self.assertTrue(e2.issubset(result))

    def test_three_layers_union(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B')})
            p2 = self._net(d, 'l2', {('B', 'C')})
            p3 = self._net(d, 'l3', {('C', 'D')})
            result = _run_set_op([p1, p2, p3], 'OR')
            self.assertEqual(result, {('A', 'B'), ('B', 'C'), ('C', 'D')})


class TestNotOperation(unittest.TestCase):
    def _net(self, d, name, edges):
        path = os.path.join(d, name + '.net')
        _write_net_file(path, name, NODES, edges)
        return path

    def test_removes_shared_edges(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B'), ('B', 'C')})
            p2 = self._net(d, 'l2', {('B', 'C')})
            result = _run_set_op([p1, p2], 'NOT')
            self.assertEqual(result, {('A', 'B')})

    def test_empty_when_all_shared(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B')})
            p2 = self._net(d, 'l2', {('A', 'B')})
            result = _run_set_op([p1, p2], 'NOT')
            self.assertEqual(result, set())

    def test_unchanged_when_no_overlap(self):
        e1 = {('A', 'B'), ('B', 'C')}
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', e1)
            p2 = self._net(d, 'l2', {('C', 'D')})
            result = _run_set_op([p1, p2], 'NOT')
            self.assertEqual(result, e1)

    def test_asymmetric_not_commutative(self):
        with tempfile.TemporaryDirectory() as d:
            p1 = self._net(d, 'l1', {('A', 'B'), ('B', 'C')})
            p2 = self._net(d, 'l2', {('B', 'C'), ('C', 'D')})
            result_ab = _run_set_op([p1, p2], 'NOT')   # l1 - l2
            result_ba = _run_set_op([p2, p1], 'NOT')   # l2 - l1
            self.assertNotEqual(result_ab, result_ba)


if __name__ == '__main__':
    unittest.main()
