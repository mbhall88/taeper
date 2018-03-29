"""Tests for `taeper` package."""
import unittest
from taeper import taeper


class TestZuluToEpochTime(unittest.TestCase):
    """Test Zulu to Epoch converter function."""
    def test_ExampleFromRead_CorrectTimeInSeconds(self):
        """Simple test case"""
        zulu_time = "2018-01-03T16:45:30Z"
        result = taeper._zulu_to_epoch_time(zulu_time)
        expected = 1514997930.0
        self.assertEqual(result, expected)


class TestExtractTimeFields(unittest.TestCase):
    """Test function that extracts time info from fast5 files"""
    def test_Read9Fast5TestFile_CorrectFieldsExtracted(self):
        test_fast5 = 'tests/data/pass/read9.fast5'
        result = taeper.extract_time_fields(test_fast5)
        expected = {
            'exp_start_time': 1514997930.0,
            'sampling_rate': 4000.0,
            'duration': 19922.0,
            'start_time': 28238530.0
        }
        self.assertDictEqual(result, expected)
