"""Tests for `taeper` package."""
import unittest
import pathlib
import logging
from taeper import taeper

logging.disable(logging.CRITICAL)


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
        """Test fields in read9"""
        test_fast5 = 'tests/data/pass/read9.fast5'
        result = taeper.extract_time_fields(test_fast5)
        expected = {
            'exp_start_time': 1514997930.0,
            'sampling_rate': 4000.0,
            'duration': 19922.0,
            'start_time': 28238530.0
        }
        self.assertDictEqual(result, expected)

    def test_OldFast5File_EmptyDict(self):
        test_fast5 = 'tests/data/old.fast5'
        result = taeper.extract_time_fields(test_fast5)
        expected = {}
        self.assertDictEqual(result, expected)


class TestCalculateTimestamp(unittest.TestCase):
    """Make sure timestamps are calculated correctly"""

    def test_Read8TimestampIsExactlyCorrect(self):
        test_fast5 = 'tests/data/pass/read8.fast5'
        result = taeper.calculate_timestamp(test_fast5)
        expected = 1515004995.93975  # calculated by hand
        self.assertEqual(result, expected)

    def test_OldFast5_Zero(self):
        test_fast5 = 'tests/data/old.fast5'
        result = taeper.calculate_timestamp(test_fast5)
        expected = 0
        self.assertEqual(result, expected)


class TestScantree(unittest.TestCase):
    """Test scantree functiion"""

    def test_TestOnlyFast5FilesReturned_NoCornerCaseFile(self):
        """Test on tests/data directory"""
        ext = '.fast5'
        path = 'tests'
        result = list(taeper.scantree(path, ext))
        expected = [
            'tests/data/fail/empty.fast5',
            'tests/data/fail/read0.fast5',
            'tests/data/fail/read6.fast5',
            'tests/data/old.fast5',
            'tests/data/pass/random.fast5',
            'tests/data/pass/read1.fast5',
            'tests/data/pass/read2.fast5',
            'tests/data/pass/read3.fast5',
            'tests/data/pass/read4.fast5',
            'tests/data/pass/read5.fast5',
            'tests/data/pass/read7.fast5',
            'tests/data/pass/read8.fast5',
            'tests/data/pass/read9.fast5'
        ]
        for x, y in zip(expected, result):
            self.assertEqual(x, y)

    def test_TestCaseExtension_ReturnOnlyCornerCase(self):
        """Test for only corner case"""
        ext = '.case'
        path = 'tests'
        result = list(taeper.scantree(path, ext))
        expected = ['tests/data/corner.case', 'tests/data/fail/corner.case']
        for x, y in zip(expected, result):
            self.assertEqual(x, y)


class TestFilterList(unittest.TestCase):
    """Test filter list function"""

    def test_ListWithNoNoneOrEmptyList_NoChange(self):
        xs = [1, 2, 3]
        result = taeper.filter_list(xs)
        expected = [1, 2, 3]
        self.assertListEqual(result, expected)

    def test_ListWithNoneButNoEmptyList_FilterOutNone(self):
        xs = [1, 2, None, 3]
        result = taeper.filter_list(xs)
        expected = [1, 2, 3]
        self.assertListEqual(result, expected)

    def test_ListWithNoNoneButEmptyList_FilterOutEmptyList(self):
        xs = [1, 2, [], 3]
        result = taeper.filter_list(xs)
        expected = [1, 2, 3]
        self.assertListEqual(result, expected)

    def test_ListWithNoneAndEmptyList_FilterOutEmptyListAndNone(self):
        xs = [1, None, 2, [], 3]
        result = taeper.filter_list(xs)
        expected = [1, 2, 3]
        self.assertListEqual(result, expected)

    def test_EmptyList_ReturnEmptyList(self):
        xs = []
        result = taeper.filter_list(xs)
        expected = []
        self.assertListEqual(result, expected)

    def test_ListWithOnlyNone_ReturnEmptyList(self):
        xs = [None]
        result = taeper.filter_list(xs)
        expected = []
        self.assertListEqual(result, expected)

    def test_ListWithOnlyEmptyList_ReturnEmptyList(self):
        xs = [[]]
        result = taeper.filter_list(xs)
        expected = []
        self.assertListEqual(result, expected)


class TestCentreList(unittest.TestCase):
    """Test centre list function"""

    def test_GeneralCase(self):
        xs = [[4, 'a'], [7, 'b'], [10, 'c']]
        result = taeper.centre_list(xs)
        expected = [(0, 'a'), (3, 'b'), (3, 'c')]
        self.assertListEqual(result, expected)


class TestGenerateIndex(unittest.TestCase):
    """Test the function that generates the index"""

    def test_TestFast5Files(self):
        test_dir = 'tests/data'
        result = taeper.generate_index(test_dir)
        expected = [
            (0.0, 'tests/data/pass/random.fast5'),
            (24839288.405, 'tests/data/pass/read7.fast5'),
            (7.476, 'tests/data/pass/read9.fast5'),
            (1.327, 'tests/data/pass/read8.fast5'),
            (6.065, 'tests/data/pass/read3.fast5'),
            (18.221, 'tests/data/pass/read2.fast5'),
            (34.035, 'tests/data/fail/read6.fast5'),
            (3.294, 'tests/data/pass/read1.fast5'),
            (0.126, 'tests/data/pass/read5.fast5'),
            (8.73, 'tests/data/fail/read0.fast5'),
            (0.235, 'tests/data/pass/read4.fast5')
        ]
        self.assertListEqual(result, expected)


class TestLoadIndex(unittest.TestCase):
    """Test the loading of an index file"""

    def test_LoadIndex_SameAsGeneratedIndex(self):
        test_index = 'tests/data/taeper_index.npy'
        result = taeper.load_index(test_index)
        expected = [
            (0.0, 'tests/data/pass/random.fast5'),
            (24839288.405, 'tests/data/pass/read7.fast5'),
            (7.476, 'tests/data/pass/read9.fast5'),
            (1.327, 'tests/data/pass/read8.fast5'),
            (6.065, 'tests/data/pass/read3.fast5'),
            (18.221, 'tests/data/pass/read2.fast5'),
            (34.035, 'tests/data/fail/read6.fast5'),
            (3.294, 'tests/data/pass/read1.fast5'),
            (0.126, 'tests/data/pass/read5.fast5'),
            (8.73, 'tests/data/fail/read0.fast5'),
            (0.235, 'tests/data/pass/read4.fast5')
        ]
        self.assertListEqual(result, expected)


class TestGenerateOutputFilepath(unittest.TestCase):
    """Test generate_output_filepath function"""

    def test_NoInputStructureToKeep_OutputPlusFilename(self):
        filepath = 'tests/data/read.fast5'
        input_dir = 'tests/data'
        output_dir = 'tests/data/tmp'
        result = taeper.generate_output_filepath(filepath, output_dir,
                                                 input_dir)
        expected = pathlib.Path('tests/data/tmp/read.fast5')
        self.assertEqual(result, expected)

    def test_InputStructureToKeep_OutputPlusFilenamePlusStructure(self):
        filepath = 'tests/data/pass/read.fast5'
        input_dir = 'tests/data'
        output_dir = 'tests/data/tmp'
        result = taeper.generate_output_filepath(filepath, output_dir,
                                                 input_dir)
        expected = pathlib.Path('tests/data/tmp/pass/read.fast5')
        self.assertEqual(result, expected)
