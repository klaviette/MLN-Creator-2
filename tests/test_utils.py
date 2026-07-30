"""
Tests for tkinter/utils.py — file helpers and option lists.
"""
import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tkinter'))
from utils import (
    get_file_labels,
    get_filename,
    get_similarity_metric_options,
    get_feature_type_options,
)


class TestGetFileLabels(unittest.TestCase):
    def _make_csv(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_returns_correct_headers(self):
        path = self._make_csv('id,name,age\n1,Alice,30\n')
        try:
            self.assertEqual(get_file_labels(path), ['id', 'name', 'age'])
        finally:
            os.unlink(path)

    def test_single_column(self):
        path = self._make_csv('only_col\n1\n2\n')
        try:
            self.assertEqual(get_file_labels(path), ['only_col'])
        finally:
            os.unlink(path)

    def test_many_columns(self):
        headers = ['a', 'b', 'c', 'd', 'e']
        path = self._make_csv(','.join(headers) + '\n1,2,3,4,5\n')
        try:
            self.assertEqual(get_file_labels(path), headers)
        finally:
            os.unlink(path)

    def test_headers_with_spaces(self):
        path = self._make_csv('first name,last name\nAlice,Smith\n')
        try:
            labels = get_file_labels(path)
            self.assertIn('first name', labels)
            self.assertIn('last name', labels)
        finally:
            os.unlink(path)


class TestGetFilename(unittest.TestCase):
    def test_posix_path(self):
        self.assertEqual(get_filename('/some/path/to/file.csv'), 'file.csv')

    def test_forward_slash_windows_style(self):
        self.assertEqual(get_filename('C:/Users/user/data.csv'), 'data.csv')

    def test_filename_only(self):
        self.assertEqual(get_filename('myfile.csv'), 'myfile.csv')

    def test_preserves_extension(self):
        self.assertEqual(get_filename('/path/to/archive.tar.gz'), 'archive.tar.gz')


class TestGetSimilarityMetricOptions(unittest.TestCase):
    def test_returns_list(self):
        self.assertIsInstance(get_similarity_metric_options(), list)

    def test_contains_all_expected_metrics(self):
        opts = get_similarity_metric_options()
        for metric in ['EQUALITY', 'EUCLIDEAN', 'HAVERSINE', 'JACCARD', 'COSINE']:
            with self.subTest(metric=metric):
                self.assertIn(metric, opts)

    def test_non_empty(self):
        self.assertGreater(len(get_similarity_metric_options()), 0)


class TestGetFeatureTypeOptions(unittest.TestCase):
    def test_returns_list(self):
        self.assertIsInstance(get_feature_type_options(), list)

    def test_contains_all_expected_types(self):
        opts = get_feature_type_options()
        for ft in ['NOMINAL', 'NUMERIC', 'GEOGRAPHIC', 'TIME', 'DATE', 'SET', 'TEXT']:
            with self.subTest(feature_type=ft):
                self.assertIn(ft, opts)

    def test_non_empty(self):
        self.assertGreater(len(get_feature_type_options()), 0)


if __name__ == '__main__':
    unittest.main()
