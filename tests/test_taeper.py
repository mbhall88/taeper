"""Tests for `taeper` package."""
import unittest
from taeper import taeper


class TestZuluToEpochTime(unittest.TestCase):
    """Tests for `taeper` package."""

    def test_ExampleFromRead_CorrectTimeInSeconds(self):
        """Set up test fixtures, if any."""
        zulu_time = "2018-01-03T16:45:30Z"
        result = taeper._zulu_to_epoch_time(zulu_time)
        expected = 1514997930.0
        self.assertEqual(result, expected)


