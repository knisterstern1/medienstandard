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
import getopt
import json
import os
from pathlib import Path, PosixPath
import re
import sys
import urllib
from typing import List

# my modules
from result import Result
from rule import Rule

DEBUG = False 

class MediaStandard:
    """This class represents a certain version of the mediastandard
    """

    def __init__(self): 
        self.version = "3.0"
        self.rules = []

    def check_filename(self, path: PosixPath) ->Result: 
        """Check if filename conforms to rules
        """
        result = None
        for rule in self.rules:
            result = rule.applies(path.name) 
            if not result.check_passed:
                return result
        m = self.pattern.match(path.name)
        if m is not None:
            result = Result(True, '',m.groupdict())
        return result

    def check_content(self, result: Result) ->Result: 
        """Check if filename conforms to rules
        """
        for key in result.groups.keys():
            if key in self.content.keys():
                label = self.vocabulary[key] if key in self.vocabulary.keys() else key
                print(f'{label}: {self.content[key][result.groups[key]]}')
        return result


    def load(self, json_file, verbose=False, colorkey=''):
        """Load a specific standard
        """
        style_reset = '\x1b[0m' if colorkey != '' else ''
        with open(json_file) as json_ref:
            data = json.load(json_ref)
            self.version = data['info']['version']
            self.year = data['info']['year']
            self.pattern = re.compile(urllib.parse.unquote(data['pattern']))
            self.content = data['content']
            self.vocabulary = data['vocabulary']
            for rule in data['rules']:
                self.rules.append(Rule(rule))
        print(colorkey + f"Medienstandard Version {self.version}, {self.year} geladen ..." + style_reset)
        if verbose:
            print(colorkey + data['comment'] + style_reset)


