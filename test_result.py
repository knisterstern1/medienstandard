import unittest
from pathlib import Path
from colorama import Fore

# my module
from result import Result
from rule import Rule


class TestRule(unittest.TestCase):

    def testResult(self):
        ruleDict = {"regex":"%5E%5Ba-z0-9_%5C-%5D%2A%5C.%5Ba-z0-9_%5C-%5D%2A%24","error":"Ungültige Zeichen","onError": [{"regex":".*[A-Z].*","error":"Grossbuchstaben!"}]}
        rule = Rule(ruleDict)
        result = rule.applies('pd31_v007004_2022-05-20_Museumsnacht-2022_s-031.jpg')
        self.assertEqual(result.check_passed, False)
        self.assertTrue(ruleDict['onError'][0]['error'] in result.error_msg)


if __name__ == "__main__":
    unittest.main()
