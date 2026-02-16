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
from urllib import parse
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

    def get_content(self, result: Result) ->dict:
        """Return a dict with all the information.
        """
        information = {}
        for key in result.groups.keys():
            if key in self.content.keys():
                label = self.vocabulary[key] if key in self.vocabulary.keys() else key
                combinedCategory = None
                if not result.groups[key] in self.content[key].keys():
                    if result.groups[key][0] in self.content.keys() and result.groups[key][1] in self.content[result.groups[key][0]].keys() and result.groups[key][2] in self.content[result.groups[key][0]].keys():
                        combinedCategory = { "key": result.groups[key][0], "parent": key }
                    else:
                        raise Exception(f'{result.groups[key]} not in "{label}"')
                if key == 'areaCategory' and result.groups[key][0] in self.content['area'].keys():
                    information['area'] = { "label": "Bereich", "text": self.content["area"][result.groups[key][0]] } 
                    if combinedCategory is not None:
                        combinedCategory['parent'] = 'area'
                    label = 'Kategorie'
                if combinedCategory is not None:
                    contents = []
                    labels = [ label, self.content['mappingCategoryLabel'][combinedCategory['key']] ] 
                    for index in [ 1, 2]:
                        contents.append({ "label": labels[index-1], "text": self.content[combinedCategory['key']][result.groups[key][index]]})
                    information[combinedCategory['parent']]['contents'] = contents 
                else:
                    information[key] = { "label": label, "text": self.content[key][result.groups[key]] }
        return information


    def load(self, json_file, verbose=False, color_dict=None):
        """Load a specific standard
        """
        style_reset = '' if color_dict is None or 'reset' not in color_dict.keys() else color_dict['reset']
        if color_dict is None:
            color_dict = { "default":"", "comment": "" }
        with open(json_file, encoding='utf-8') as json_ref:
            data = json.load(json_ref)
            self.version = data['info']['version']
            self.year = data['info']['year']
            self.pattern = re.compile(parse.unquote(data['pattern']))
            self.content = data['content']
            self.vocabulary = data['vocabulary']
            for rule in data['rules']:
                self.rules.append(Rule(rule))
        print(color_dict['default'] + f"Medienstandard Version {self.version}, {self.year} geladen ..." + style_reset)
        if verbose:
            print(color_dict['comment'] + data['comment'] + style_reset)


