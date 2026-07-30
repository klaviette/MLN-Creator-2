"""
Tests for scripts/confgen.py — the .gen config file generator.
"""
import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from confgen import confgen


class TestConfgenCreatesFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        data_dir = os.path.join(self.tmpdir.name, 'datasets', 'test', 'data_files')
        os.makedirs(data_dir)
        self.csv_path = os.path.join(data_dir, 'sample.csv')
        with open(self.csv_path, 'w') as f:
            f.write('id,name,value\n1,Alice,10\n2,Bob,20\n')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_returns_path_to_gen_file(self):
        out = confgen(self.csv_path, 'name_layer', ['id'], 'name', 'NOMINAL', 'EQUALITY', 'NULL')
        self.assertTrue(os.path.exists(out))
        self.assertTrue(out.endswith('.gen'))

    def test_gen_file_placed_in_data_files_dir(self):
        out = confgen(self.csv_path, 'name_layer', ['id'], 'name', 'NOMINAL', 'EQUALITY', 'NULL')
        self.assertEqual(os.path.dirname(out), os.path.dirname(self.csv_path))

    def test_layers_generated_dir_created(self):
        confgen(self.csv_path, 'name_layer', ['id'], 'name', 'NOMINAL', 'EQUALITY', 'NULL')
        layers_dir = os.path.join(self.tmpdir.name, 'datasets', 'test', 'layers_generated')
        self.assertTrue(os.path.isdir(layers_dir))


class TestConfgenFileContent(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        data_dir = os.path.join(self.tmpdir.name, 'datasets', 'test', 'data_files')
        os.makedirs(data_dir)
        self.csv_path = os.path.join(data_dir, 'sample.csv')
        with open(self.csv_path, 'w') as f:
            f.write('id,name,value\n1,Alice,10\n2,Bob,20\n')

    def tearDown(self):
        self.tmpdir.cleanup()

    def _read_gen(self, **kwargs):
        out = confgen(self.csv_path, **kwargs)
        with open(out) as f:
            return f.read()

    def test_required_fields_present(self):
        content = self._read_gen(
            layer_name='value_layer', primary_key_columns=['id'],
            feature_column='value', feature_type='NUMERIC',
            similarity_metric='EUCLIDEAN', threshold='5.0',
        )
        self.assertIn('INPUT_FILE_NAME= sample.csv', content)
        self.assertIn('LAYER_NAME=value_layer', content)
        self.assertIn('FEATURE_COLUMN=value', content)
        self.assertIn('FEATURE_TYPE=NUMERIC', content)
        self.assertIn('SIMILARITY_METRIC=EUCLIDEAN', content)
        self.assertIn('THRESHOLD=5.0', content)
        self.assertIn('BEGIN_LAYER', content)
        self.assertIn('END_LAYER', content)

    def test_multiple_primary_keys_comma_separated(self):
        content = self._read_gen(
            layer_name='test_layer', primary_key_columns=['id', 'name'],
            feature_column='value', feature_type='NOMINAL',
            similarity_metric='EQUALITY', threshold='NULL',
        )
        self.assertIn('PRIMARY_KEY_COLUMN=id,name', content)

    def test_null_threshold_written_as_null(self):
        content = self._read_gen(
            layer_name='test_layer', primary_key_columns=['id'],
            feature_column='name', feature_type='NOMINAL',
            similarity_metric='EQUALITY', threshold='NULL',
        )
        self.assertIn('THRESHOLD=NULL', content)

    def test_geographic_optional_params_written(self):
        content = self._read_gen(
            layer_name='geo_layer', primary_key_columns=['id'],
            feature_column='loc', feature_type='GEOGRAPHIC',
            similarity_metric='HAVERSINE', threshold='10.0',
            longitude_col='lon', latitude_col='lat',
        )
        self.assertIn('LONGITUDE_FEATURE_COLUMN=lon', content)
        self.assertIn('LATITUDE_FEATURE_COLUMN=lat', content)

    def test_date_optional_params_written(self):
        content = self._read_gen(
            layer_name='date_layer', primary_key_columns=['id'],
            feature_column='date', feature_type='DATE',
            similarity_metric='EQUALITY', threshold='NULL',
            date_format='dd-mm-yyyy', date_metric='MONTH',
        )
        self.assertIn('DATE_FORMAT=dd-mm-yyyy', content)
        self.assertIn('DATE_METRIC=MONTH', content)

    def test_time_optional_params_written(self):
        content = self._read_gen(
            layer_name='time_layer', primary_key_columns=['id'],
            feature_column='time', feature_type='TIME',
            similarity_metric='EUCLIDEAN', threshold='30',
            time_format='hh:mm',
        )
        self.assertIn('TIME_FORMAT=hh:mm', content)

    def test_range_and_multi_range_written(self):
        content = self._read_gen(
            layer_name='num_layer', primary_key_columns=['id'],
            feature_column='value', feature_type='NUMERIC',
            similarity_metric='EUCLIDEAN', threshold='NULL',
            range_val='[1,10]', multi_range='[1,3]-[7,9]', num_segments='3',
        )
        self.assertIn('RANGE=[1,10]', content)
        self.assertIn('MULTI_RANGE=[1,3]-[7,9]', content)
        self.assertIn('NUMBER_OF_EQUI_SIZED_SEGMENTS=3', content)

    def test_input_output_directory_lines_present(self):
        content = self._read_gen(
            layer_name='test_layer', primary_key_columns=['id'],
            feature_column='value', feature_type='NOMINAL',
            similarity_metric='EQUALITY', threshold='NULL',
        )
        self.assertIn('INPUT_DIRECTORY=', content)
        self.assertIn('OUTPUT_DIRECTORY=', content)
        self.assertIn('USERNAME=default', content)


if __name__ == '__main__':
    unittest.main()
