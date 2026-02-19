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
    def print_default(self, output: str):
        print(output)
    def print_comment(self, output: str):
        print(output)
    def print_comment(self, output: str):
        print(output)
    def print_highlight(self, output: str):
        print(output)
    def print_fail(self, filename: str, error_msg: str, verbose: bool):
        if verbose:
            print(f'{filename}\t[FAIL]:\t{error_msg}')
        else:
            print(f'{filename}\t[FAIL]')
    def print_file_info(self, filename: str, information: dict, verbose: bool):
        """Display the information
        """
        if verbose:
            print(f'Informationen zu {filename}: ')
            for key in information.keys():
                print(f'\t{information[key]["label"]}:\t{information[key]["text"]}')
                if 'contents' in information[key].keys():
                    for content in information[key]['contents']:
                        print(f'\t{content["label"]}:\t{content["text"]}')
        else:
            print(f'{filename}\t[OK]')


    def get_filename(self, file_path: PosixPath) ->str:
        return file_path.absolute() if file_path.exists() else file_path.name


def usage():
    """prints information on how to use the script
    """
    print(main.__doc__)

def validate(args: List[str], printer: Printer, json: str, verbose: bool, failOnly: bool, patternOnly: bool):
    """Validate the input.
    """
    #TODO: add everything from main
    checker = MediaStandard()
    if checker.load(json) == 0:
        printer.print_default(f"Medienstandard Version {checker.version}, {checker.year} geladen ...")
        if verbose:
            printer.print_default(f'"[Quelldatei: {json}]')
            for comment in checker.comments:
                print(f'\n{comment}')
    if patternOnly:
        print(checker.pattern.pattern)
        return 0


def main(argv):
    """This program can be used to check whether filenames accord with a media standard. It does not rely on fancy packages.

    simple_mediastandard_validation.py [OPTIONS] file1 file2 ... | directory

    OPTIONS:
        -f|--fail-only  show only fails
        -h|--help       show help
        -j|--json=file  json file
        -p|--pattern    print regex pattern for mediastandard
        -v|--verbose    print infomation about json
    
        :return: exit code (int)
    """
    json="medienstandard_v3_regex.json"
    verbose = False
    failOnly = False
    patternOnly = False
    try:
        opts, args = getopt.getopt(argv, "fhj:pv", ["fail-only", "help","json=", "pattern", "verbose"])
    except getopt.GetoptError:
        usage()
        return 2
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            return 0
        elif opt in ('-f', '--fail-only'):
            failOnly = True 
        elif opt in ('-v', '--verbose'):
            verbose = True 
        elif opt in ('-p', '--pattern'):
            patternOnly = True 
        elif opt in ('-j', '--json'):
            json = arg
    checker = MediaStandard()
    printer = Printer()
    if checker.load(json) == 0:
        printer.print_default(f"Medienstandard Version {checker.version}, {checker.year} geladen ...")
        if verbose:
            for comment in checker.comments:
                print(f'\n{comment}')
    if patternOnly:
        print(checker.pattern.pattern)
        return 0

    filenames = get_filenames([ Path(arg) for arg in args ])
    
    print(f'Checking {len(filenames)} filename{"s" if len(filenames) > 1 else ""}.')
    if len(filenames) < 1:
        print('Nothing to do ...')
        usage()
    color_dict = { "fail": '', "default": '', "reset": ''  }
    for file_path in filenames: 
        result = checker.check_filename(file_path)
        if not result.check_passed:
            filename = result.getFilenameInfo(file_path, color_dict)
            if verbose:
                print(f'{filename}\t[FAIL]: {result.error_msg}')
            else:
                print(f'{filename}\t[FAIL]')
        else:
            filename = file_path.absolute() if file_path.exists() else file_path.name
            try: 
                information = checker.get_content(result)
                if not failOnly:
                    if verbose:
                        print(f'Informationen zu {filename}: ')
                        print_information(information)
                    else:
                        print(f'{filename}\t[OK]')
            except Exception as e:
                if verbose:
                    print(f'{filename}\t[FAIL]: {e}')
                else:
                    print(f'{filename}\t[FAIL]')
    return 0 

def print_information(information: dict):
    """Display the information
    """
    for key in information.keys():
        print(f'\t{information[key]["label"]}:\t{information[key]["text"]}')
        if 'contents' in information[key].keys():
            for content in information[key]['contents']:
                print(f'\t{content["label"]}:\t{content["text"]}')

def get_filenames(paths: List[PosixPath]) -> List[PosixPath]:
    """Get a list of filenames from input arguments
    """
    filenames = []
    for file_path in paths:
        if file_path.is_dir():
            for filename in get_filenames(list(file_path.glob('*'))):
                filenames.append(filename)
        else:
            filenames.append(file_path)
    return filenames

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

