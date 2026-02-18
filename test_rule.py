import unittest

# my module
from rule import Rule


class TestRule(unittest.TestCase):

    def testRule(self):
        ruleDict = {"regex":"%5E%5Ba-z0-9_%5C-%5D%2A%5C.%5Ba-z0-9_%5C-%5D%2A%24","error":"Ungültige Zeichen","onError": [{"regex":".*[A-Z].*","error":"Grossbuchstaben!"}]}
        rule = Rule(ruleDict)
        result = rule.applies('pd31_v007004_2022-05-20_Museumsnacht-2022_s-031.jpg')
        self.assertEqual(result.check_passed, False)
        self.assertTrue(ruleDict['onError'][0]['error'] in result.error_msg)
        ruleDict = {"regex":"%5E.%7B4%7D%28_%5Barlpsvz%5Cd%5D%5Cd%7B6%7D%29%2A_%5Cd%7B4%7D-%5Cd%7B2%7D-%5Cd%7B2%7D_.%2A","error":"Objektreferenz."}
        rule = Rule(ruleDict)
        result = rule.applies('pd31_2022-05-20_museumsnacht-2022_s-031.jpg')
        self.assertEqual(result.check_passed, True)


if __name__ == "__main__":
    unittest.main()
