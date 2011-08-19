import os
import hashlib
from innovate import utils

from django.test import TestCase


class UploadUtilsTest(TestCase):
    """Various tests for utilities we use when uploading files."""

    def assertEmpty(self, l):
        """Custom assertion. Test that any iterable is empty."""
        return hasattr(l, '__iter__') and len(l) == 0

    def test_directory_parititioning(self):
        """Test that files are partitioned into upload directories."""
        test = lambda r, exp, s: [exp == utils.get_partition_id(i, s)
                                  for i in range(*r)]
        all_true = lambda l: filter(lambda x: not x, l)
        self.assertEmpty(all_true(test((1, 10), 1, 10)))
        self.assertEmpty(all_true(test((11, 20), 2, 10)))
        self.assertEmpty(all_true(test((1001, 2000), 2, 1000)))

    def test_filenames(self):
        """Test that filenames are properly encoded on upload."""
        def run_battery(filename):
            safe_name = utils.safe_filename(filename)
            name, ext = os.path.splitext(safe_name)
            assert safe_name != filename
            assert len(safe_name) == 32 + len(ext)
            assert isinstance(safe_name, str)
        run_battery('index.php')
        run_battery('02134')
        run_battery(u'\x123')
        run_battery(hashlib.sha1('myimage.jpg').hexdigest())
        run_battery(hashlib.md5('myimage.jpg').hexdigest())

    def test_filenames_malicious_extension(self):
        """Ensure malicious users can't trick file encoding."""
        safe_name = utils.safe_filename('fdasfdsa.index.php')
        name, ext = os.path.splitext(safe_name)
        assert ext == '.php'
