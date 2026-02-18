#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#    Copyright (C) Christian Steiner 2026  {{{1
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/> 1}}}
from pathlib import Path, PosixPath
import re
from urllib import parse

# my module
from result import Result

DEBUG = False 

class Rule:
    """This class represents a rule of the mediastandard
    """
    def __init__(self, rule: dict): 
        self.pattern = re.compile(parse.unquote(rule['regex']))
        self.error = rule['error']
        self.onErrorRules = []
        if 'onError' in rule.keys():
            for errorRule in rule['onError']:
                self.onErrorRules.append(Rule(errorRule))

    def applies(self, filename: str) ->Result:
        """Check if rule applies, return Result
        """
        if self.pattern.match(filename):
            return Result()
        errorResult = Result(False, self.error)
        for onErrorRule in self.onErrorRules:
            m = onErrorRule.findError(filename)
            if m:
                errorResult.addMessage(onErrorRule.error, m)
        return errorResult

    def findError(self, filename: str) ->re.Match:
        """Return true if pattern matches
        """
        return self.pattern.match(filename)


