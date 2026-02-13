import unittest
from pathlib import Path

# my module
from mediastandard import MediaStandard
from mediastandard_validation import get_filenames


class TestMediastandard(unittest.TestCase):
    def setUp(self):
        self.checker = MediaStandard()
        self.checker.load('medienstandard_v3_regex.json')

    def testLoad(self):
        self.assertEqual(self.checker.version, '3.0.1')

    def test_check_filename(self):
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnacht-2022_s-031.jpg'))
        self.assertTrue(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnöcht-2022_s-031.jpg'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsn cht-2022_s-031.jpg'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnncht-2022_s-031.jp'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('zd31_v007004_2022-05-20_museumsnacht-2022_s-031.jp'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pu31_v007004_2022-05-20_museumsnacht-2022_s-031.jp'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd312_v007004_2022-05-20_museumsnacht-2022_s-031.jp'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_asfd_s-asfd_asfd_asf.jp'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnacht-2022.s-031.jpg'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnacht-2022_s-031.lasjg'))
        self.assertFalse(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnacht-2022_s-031.lasjg'))
        self.assertFalse(result.check_passed)
        print(result.error_msg)

    def test_get_filenames(self):
        paths = [ Path('test_dir') ]
        filenames = get_filenames(paths)
        self.assertEqual(len(filenames), 8)

if __name__ == "__main__":
    unittest.main()
