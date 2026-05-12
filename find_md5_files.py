#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This program can be used to find all md5 checksum files in a folder and print a CSV mapping file.
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
import csv 
import os
from pathlib import Path, PosixPath
import re
import sys
from typing import List


def parse_options(argv: List[str]) ->dict:
    """

    OPTIONS:
        -h|--help                        show help
        -e|--extensions=ext1+ext2+ext3   file extensions to include
        -v|--verbose                     print infomation

    """
    options = { 'args': [], 'extensions': ['.mov', '.mp4', '.tif', '.jpg'], 'verbose': False, 'showUsage': False, 'message': 0 }
    try:
        opts, args = getopt.getopt(argv, "e:hv", ["extensions=","help","verbose"])
    except getopt.GetoptError:
        options['showUsage'] = True 
        options['message'] = 2 
        return options
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            options['showUsage'] = True 
            return options
        elif opt in ('-e', '--extensions'):
            options['extensions'] = arg.split('+')
        elif opt in ('-v', '--verbose'):
            options['verbose'] = True 
    options['args'] = args
    return options

def usage() ->int:
    """prints information on how to use the script
    """
    print("\n\t" + sys.argv[0] + " [OPTIONS] file1 file2 ... | directory")
    print(parse_options.__doc__)
    print("\t:return: exit code (int)")
    return 0

def main(argv: List[str]):
    """This program can be used to find all md5 checksum files in a folder and print a CSV mapping file."""
    arg_dict = parse_options(argv)
    if arg_dict['showUsage']:
        usage()
        return arg_dict['message']
    args = arg_dict['args']
    verbose = arg_dict['verbose']
    files = []
    bags = []
    get_files(files, bags, [ Path(arg) for arg in args ], arg_dict, verbose)
    print(files)
    print(bags)
    return 0 

def get_files(files: List[PosixPath], bags: List[PosixPath], paths: List[PosixPath], options: dict, verbose: bool):
    """Get a list of files from input arguments
    """
    for file_path in paths:
        if file_path.is_dir() and not re.match('^.*s-([a-z0-9]{1,}-)*bag$', file_path.name):
            get_files(files, bags, list(file_path.glob('*')), options, verbose)
        elif re.match('^.*s-([a-z0-9]{1,}-)*bag$', file_path.name):
            bags.append(file_path)
        elif file_path.suffix in options['extensions']:
            files.append(file_path)
            if verbose:
                print(f'{len(files)} files added ...', end='\r')

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

