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
from colorama import Fore, Style
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

def usage():
    """prints information on how to use the script
    """
    print(main.__doc__)

def main(argv):
    """This program can be used to check whether filenames accord with a media standard.

    mediastandard_validation.py [OPTIONS] file1 file2 ... | directory

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
    color_dict = { "default": Fore.LIGHTBLUE_EX, "comment": Fore.LIGHTWHITE_EX, "fail": Fore.RED,  "reset": Style.RESET_ALL}
    if checker.load(json) == 0:
        print(color_dict['default'] + f"Medienstandard Version {checker.version}, {checker.year} geladen ..." + Style.RESET_ALL)
        if verbose:
            for comment in checker.comments:
                print(color_dict['comment'] + f'\n{comment}' + Style.RESET_ALL)
    filenames = get_filenames([ Path(arg) for arg in args ])
    if patternOnly:
        print(checker.pattern.pattern)
        return 0
    print(Fore.MAGENTA + f'Checking {len(filenames)} filename{"s" if len(filenames) > 1 else ""}.' + Style.RESET_ALL)
    if len(filenames) < 1:
        print('Nothing to do ...')
        usage()
    for file_path in filenames: 
        result = checker.check_filename(file_path)
        if not result.check_passed:
            filename = result.getFilenameInfo(file_path, color_dict)
            if verbose:
                print(f'{filename}\t[' + Fore.RED + 'FAIL' + Style.RESET_ALL + f']: {result.error_msg}')
            else:
                print(f'{filename}\t[' + Fore.RED + 'FAIL' + Style.RESET_ALL + f']')
        else:
            filename = Fore.LIGHTBLUE_EX + file_path.absolute() + Style.RESET_ALL if file_path.exists() else Fore.LIGHTBLUE_EX + file_path.name + Style.RESET_ALL
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
                    print(f'{filename}\t[' + Fore.RED + 'FAIL' + Style.RESET_ALL + f']: {e}')
                else:
                    print(f'{filename}\t[' + Fore.RED + 'FAIL' + Style.RESET_ALL + f']')
    return 0 

def print_information(information: dict):
    """Display the information
    """
    for key in information.keys():
        print(f'\t{information[key]["label"]}:\t' + Fore.LIGHTBLUE_EX + f'{information[key]["text"]}' + Style.RESET_ALL)
        if 'contents' in information[key].keys():
            for content in information[key]['contents']:
                print(f'\t{content["label"]}:\t'  + Fore.LIGHTBLUE_EX + f'{content["text"]}' + Style.RESET_ALL)

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

