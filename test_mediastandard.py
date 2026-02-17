import unittest
from colorama import Fore
from pathlib import Path
import sys

# my module
from mediastandard import MediaStandard
from mediastandard_validation import print_information


class TestMediastandard(unittest.TestCase):
    def setUp(self):
        self.checker = MediaStandard()
        self.checker.load('medienstandard_v3_regex.json')

    def testLoad(self):
        self.assertEqual(self.checker.version, '3.0.1')

    def test_get_content(self):
        result = self.checker.check_filename(Path('kw1a_v007004_2022-05-20_museumsnacht-2022_s-031.jpg'))
        information = self.checker.get_content(result)
        self.assertEqual(information['ids']['contents'][0]['text'], '7004')
        result = self.checker.check_filename(Path('kw1a_0007004_2022-05-20_museumsnacht-2022_s-031.jpg'))
        information = self.checker.get_content(result)
        self.assertEqual(information['ids']['contents'][0]['text'], '7004')
        result = self.checker.check_filename(Path('kw1a_x007004_2022-05-20_museumsnacht-2022_s-031.jpg'))
        with self.assertRaises(Exception):
            self.checker.get_content(result)

    def test_parse_title(self):
        information = self.checker.parse_title('_asdf-asdf', 'test')
        self.assertEqual(information['text'], 'Asdf Asdf')

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
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnacht-2022_s-031.la3'))
        self.assertTrue(result.check_passed)
        result = self.checker.check_filename(Path('pd31_v007004_2022-05-20_museumsnacht-2022_s-031.lasjg'))
        self.assertFalse(result.check_passed)
        print(result.error_msg)


if __name__ == "__main__":
    unittest.main()
