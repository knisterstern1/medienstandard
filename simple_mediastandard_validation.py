#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This program can be used to check whether the filename of files accords with the mediastandard.
"""
#    Copyright (C) Christian Steiner 2025  {{{1
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
from mediastandard import MediaStandard

DEBUG = False 

class Printer:
    """This class represents a simple output printer.
    """
    def __init__(self): 
        self.color_dict = { "fail": '', "default": '', "reset": '', 'comment':'', 'highlight':''  }
    def get_filename(self, file_path: PosixPath) ->str:
        return file_path.absolute() if file_path.exists() else file_path.name
    def print_default(self, output: str):
        print(self.color_dict['default'] + output + self.color_dict['reset'])
    def print_comment(self, output: str):
        print(self.color_dict['comment'] + output + self.color_dict['reset'])
    def print_highlight(self, output: str):
        print(self.color_dict['highlight'] + output + self.color_dict['reset'])
    def print_fail(self, filename: str, error_msg: str, verbose: bool):
        if verbose:
            print(f'{filename}\t[' + self.color_dict['fail'] + 'FAIL' + self.color_dict['reset'] + f']:\t{error_msg}')
        else:
            print(f'{filename}\t[' + self.color_dict['fail'] + 'FAIL' + self.color_dict['reset'] + ']')
    def print_information(self, filename: str, information: dict, verbose: bool):
        """Display the information
        """
        if verbose:
            print(f'Informationen zu {filename}: ')
            for key in [ key for key in information.keys() if key != 'filename']:
                print(self.color_dict['default'] + f'\t{information[key]["label"]}' + self.color_dict['reset'] + f':\t{information[key]["text"]}')
                if 'contents' in information[key].keys():
                    for content in information[key]['contents']:
                        print(self.color_dict['default'] + f'\t{content["label"]}' + self.color_dict['reset'] + f':\t{content["text"]}')
        else:
            print(f'{filename}\t[OK]')

def parse_options(argv: List[str]) ->dict:
    """

    OPTIONS:
        -f|--fail-only  show only fails
        -h|--help       show help
        -j|--json=file  json file
        -p|--pattern    print regex pattern for mediastandard
        -v|--verbose    print fileinfomation

    """
    options = { 'args': [], 'json': "medienstandard_v3_regex.json", 'verbose': False, 'failOnly': False, 'patternOnly': False, 'showUsage': False, 'message': 0 }
    try:
        opts, args = getopt.getopt(argv, "fhj:pv", ["fail-only", "help","json=", "pattern", "verbose"])
    except getopt.GetoptError:
        options['showUsage'] = True 
        options['message'] = 2 
        return options
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            options['showUsage'] = True 
            return options
        elif opt in ('-f', '--fail-only'):
            options['failOnly'] = True 
        elif opt in ('-v', '--verbose'):
            options['verbose'] = True 
        elif opt in ('-p', '--pattern'):
            options['patternOnly'] = True 
        elif opt in ('-j', '--json'):
            options['json'] = arg 
    options['args'] = args
    return options

def usage():
    """prints information on how to use the script
    """
    extra_doc = "It does not rely on fancy packages." if __name__ == "__main__" else ''
    print(main.__doc__ + " " + extra_doc)
    print("\n\t" + sys.argv[0] + " [OPTIONS] file1 file2 ... | directory")
    print(parse_options.__doc__)
    print("\t:return: exit code (int)")

def validate(printer: Printer, arg_dict: dict) ->int:
    """Validate the input.
    """
    args = arg_dict['args']
    json = arg_dict['json']
    verbose = arg_dict['verbose']
    patternOnly = arg_dict['patternOnly']
    failOnly = arg_dict['failOnly']
    checker = MediaStandard()
    if checker.load(json) == 0:
        printer.print_default(f"Medienstandard Version {checker.version}, {checker.year} geladen ...")
        if verbose or patternOnly:
            printer.print_default(f'[Quelldatei: {json}]')
            if patternOnly:
                checker.display_rules_pattern()
                return 0
            for comment in checker.comments:
                printer.print_comment(f'\n{comment}')
    filenames = []
    get_filenames(filenames, [ Path(arg) for arg in args ], checker, verbose)
    printer.print_highlight(f'Checking {len(filenames)} filename{"s" if len(filenames) > 1 else ""}.')
    if len(filenames) < 1:
        print('Nothing to do ...')
        return usage()
    for file_path in filenames: 
        result = checker.check_filename(file_path)
        if not result.check_passed:
            filename = result.getFilenameInfo(printer.color_dict)
            printer.print_fail(filename, result.error_msg, verbose)
        else:
            filename = printer.get_filename(file_path) 
            try: 
                information = checker.get_content(result)
                if not failOnly:
                    printer.print_information(filename, information, verbose)
            except Exception as e:
                printer.print_fail(filename, e, verbose)
    return 0 

def main(argv: List[str], printer: Printer):
    """This program can be used to check whether filenames accord with a media standard."""
    arg_dict = parse_options(argv)
    if arg_dict['showUsage']:
        usage()
        return arg_dict['message']
    return validate(printer, arg_dict) 

def get_filenames(filenames: List[PosixPath], paths: List[PosixPath], checker: MediaStandard, verbose: bool) -> List[PosixPath]:
    """Get a list of filenames from input arguments
    """
    for file_path in paths:
        if file_path.is_dir() and not checker.match_dir_name(file_path.name):
            get_filenames(filenames, list(file_path.glob('*')), checker, verbose)
        else:
            filenames.append(file_path)
            if verbose:
                print(f'{len(filenames)} files added ...', end='\r')

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], Printer()))

