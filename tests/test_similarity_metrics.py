"""
Tests for main/HOMLN/similarityMetric.py — SimilarityObject methods.

Requires the project's Python dependencies (numpy, scikit-learn, haversine,
nltk + punkt/stopwords data).  Run `python scripts/import_manager.py` first
if any are missing.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'main'))

# Ensure required NLTK data is available before importing SimilarityObject
try:
    import nltk
    for _find, _dl in [
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
    ]:
        try:
            nltk.data.find(_find)
        except LookupError:
            nltk.download(_dl, quiet=True)
except ImportError:
    pass

from HOMLN.similarityMetric import SimilarityObject


class TestNominalMetric(unittest.TestCase):
    """Rule 1 — EQUALITY: edge only when both values are identical."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_equal_strings_returns_edge(self):
        self.assertEqual(self.obj.nominal_metric(('Alice', 'Alice', '1,2')), '1,2')

    def test_different_strings_returns_none(self):
        self.assertIsNone(self.obj.nominal_metric(('Alice', 'Bob', '1,2')))

    def test_equal_numbers_as_strings(self):
        self.assertEqual(self.obj.nominal_metric(('42', '42', '3,4')), '3,4')

    def test_case_sensitive(self):
        self.assertIsNone(self.obj.nominal_metric(('alice', 'Alice', '1,2')))


class TestEuclideanMetric(unittest.TestCase):
    """Rule 2 — EUCLIDEAN: edge when distance < threshold."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_within_threshold_returns_edge(self):
        # sqrt((1.0-1.5)^2) = 0.5 < 1.0
        self.assertEqual(self.obj.num_metric_euclidean(('1.0', '1.5', 1.0, '1,2')), '1,2')

    def test_outside_threshold_returns_none(self):
        # sqrt((1.0-10.0)^2) = 9.0 >= 1.0
        self.assertIsNone(self.obj.num_metric_euclidean(('1.0', '10.0', 1.0, '1,2')))

    def test_identical_values_zero_distance(self):
        self.assertEqual(self.obj.num_metric_euclidean(('5.0', '5.0', 0.1, '1,2')), '1,2')

    def test_multidimensional_vectors(self):
        # sqrt((3-1)^2 + (4-1)^2) = sqrt(13) ≈ 3.6 < 4.0
        self.assertEqual(
            self.obj.num_metric_euclidean(('3,4', '1,1', 4.0, 'A,B')), 'A,B'
        )


class TestJaccardMetric(unittest.TestCase):
    """Rule 2 — JACCARD: edge when similarity > threshold."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_identical_sets_above_threshold(self):
        # jaccard(['a','b'], ['a','b']) = 1.0 > 0.5
        self.assertEqual(
            self.obj.num_metric_jaccard_similarity(('a,b', 'a,b', 0.5, '1,2')), '1,2'
        )

    def test_disjoint_sets_below_threshold(self):
        # jaccard(['a','b'], ['c','d']) = 0.0, not > 0.5
        self.assertIsNone(
            self.obj.num_metric_jaccard_similarity(('a,b', 'c,d', 0.5, '1,2'))
        )

    def test_partial_overlap(self):
        # intersection=['a'], union=['a','b','c'] → jaccard = 1/3 ≈ 0.33
        # 0.33 > 0.2 → edge returned
        self.assertEqual(
            self.obj.num_metric_jaccard_similarity(('a,b', 'a,c', 0.2, 'X,Y')), 'X,Y'
        )


class TestNumericRange(unittest.TestCase):
    """Rule 3 — RANGE: edge when both values fall inside the interval."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_inclusive_both_inside(self):
        self.assertEqual(self.obj.numeric_metric_range(('2.0', '3.0', '[1,5]', '1,2')), '1,2')

    def test_exclusive_both_inside(self):
        self.assertEqual(self.obj.numeric_metric_range(('2.0', '3.0', '(1,5)', '1,2')), '1,2')

    def test_half_open_left_exclusive(self):
        self.assertEqual(self.obj.numeric_metric_range(('2.0', '3.0', '(1,5]', '1,2')), '1,2')

    def test_half_open_right_exclusive(self):
        self.assertEqual(self.obj.numeric_metric_range(('2.0', '3.0', '[1,5)', '1,2')), '1,2')

    def test_one_value_outside_returns_none(self):
        self.assertIsNone(self.obj.numeric_metric_range(('0.0', '3.0', '[1,5]', '1,2')))

    def test_boundary_exclusive_returns_none(self):
        # value == lower bound, but lower is exclusive
        self.assertIsNone(self.obj.numeric_metric_range(('1.0', '3.0', '(1,5)', '1,2')))

    def test_boundary_inclusive_returns_edge(self):
        self.assertEqual(self.obj.numeric_metric_range(('1.0', '5.0', '[1,5]', '1,2')), '1,2')


class TestNumericMultiRange(unittest.TestCase):
    """Rule 5 — MULTI_RANGE: edge when both values fall in any of the ranges."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_values_in_first_range(self):
        self.assertEqual(
            self.obj.numeric_metric_multi_range(('2.0', '3.0', '[1,5]-[7,10]', '1,2')), '1,2'
        )

    def test_values_in_second_range(self):
        self.assertEqual(
            self.obj.numeric_metric_multi_range(('8.0', '9.0', '[1,5]-[7,10]', '1,2')), '1,2'
        )

    def test_values_in_different_ranges_returns_none(self):
        # 2.0 is in [1,5] but 8.0 is not; 8.0 is in [7,10] but 2.0 is not
        self.assertIsNone(
            self.obj.numeric_metric_multi_range(('2.0', '8.0', '[1,5]-[7,10]', '1,2'))
        )

    def test_values_outside_all_ranges_returns_none(self):
        self.assertIsNone(
            self.obj.numeric_metric_multi_range(('6.0', '6.0', '[1,5]-[7,10]', '1,2'))
        )


class TestDateEquality(unittest.TestCase):
    """Rule 7 — DATE EQUALITY: edge when the specified date component matches."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_same_day_dd_mm_yyyy(self):
        result = self.obj.numeric_metric_date_equality(
            ('15-06-2020', '15-07-2021', 'dd-mm-yyyy', 'DAY', '1,2')
        )
        self.assertEqual(result, '1,2')

    def test_different_day_dd_mm_yyyy(self):
        result = self.obj.numeric_metric_date_equality(
            ('15-06-2020', '16-06-2020', 'dd-mm-yyyy', 'DAY', '1,2')
        )
        self.assertIsNone(result)

    def test_same_month_dd_mm_yyyy(self):
        result = self.obj.numeric_metric_date_equality(
            ('01-06-2020', '15-06-2021', 'dd-mm-yyyy', 'MONTH', '1,2')
        )
        self.assertEqual(result, '1,2')

    def test_same_year_dd_mm_yyyy(self):
        result = self.obj.numeric_metric_date_equality(
            ('01-06-2020', '15-07-2020', 'dd-mm-yyyy', 'YEAR', '1,2')
        )
        self.assertEqual(result, '1,2')

    def test_different_year_returns_none(self):
        result = self.obj.numeric_metric_date_equality(
            ('01-06-2020', '15-07-2021', 'dd-mm-yyyy', 'YEAR', '1,2')
        )
        self.assertIsNone(result)

    def test_mm_dd_yyyy_format_day(self):
        result = self.obj.numeric_metric_date_equality(
            ('06-15-2020', '07-15-2021', 'mm-dd-yyyy', 'DAY', '1,2')
        )
        self.assertEqual(result, '1,2')

    def test_mm_dd_yyyy_format_month(self):
        result = self.obj.numeric_metric_date_equality(
            ('06-01-2020', '06-15-2021', 'mm-dd-yyyy', 'MONTH', '1,2')
        )
        self.assertEqual(result, '1,2')


class TestHaversineMetric(unittest.TestCase):
    """Rule 6 — HAVERSINE: edge when geographic distance < threshold (km)."""

    def setUp(self):
        self.obj = SimilarityObject()

    def test_nearby_points_within_threshold(self):
        # Two points ~1 km apart; threshold 5 km → edge
        result = self.obj.distance_cal_for_location_haversine(
            ('51.5074', '0.0', '51.5165', '0.0', 'KILOMETERS', 5.0, 'A,B')
        )
        self.assertEqual(result, 'A,B')

    def test_distant_points_outside_threshold(self):
        # London vs New York — thousands of km apart; threshold 10 km → no edge
        result = self.obj.distance_cal_for_location_haversine(
            ('51.5074', '-0.1278', '40.7128', '-74.0060', 'KILOMETERS', 10.0, 'A,B')
        )
        self.assertIsNone(result)

    def test_identical_points_zero_distance(self):
        result = self.obj.distance_cal_for_location_haversine(
            ('48.8566', '2.3522', '48.8566', '2.3522', 'KILOMETERS', 0.1, 'X,Y')
        )
        self.assertEqual(result, 'X,Y')


if __name__ == '__main__':
    unittest.main()
