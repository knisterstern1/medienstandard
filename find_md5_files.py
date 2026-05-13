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
from datetime import datetime
import getopt
import csv 
import os
from pathlib import Path, PosixPath
import re
import sys
from typing import List

EXTENSIONS = ['.mkv','.mov', '.mp4', '.tif', '.jpg']

MD5_PATTERN = re.compile(
    r"^(?:(?P<prefix>.*?)\s+)?"      # optionaler Präfix-Text + Whitespace
    r"(?P<hash>[a-fA-F0-9]{32})"     # der MD5-Hash
    r"(?:\s+(?P<filename>.+))?$",    # optionaler Dateiname nach Whitespace
    re.MULTILINE
)

def parse_options(argv: List[str]) ->dict:
    """

    OPTIONS:
        -h|--help              show help
        -v|--verbose           print infomation

    """
    options = { 'args': [], 'verbose': False, 'showUsage': False, 'message': 0 }
    try:
        opts, args = getopt.getopt(argv, "hv", ["help","verbose"])
    except getopt.GetoptError:
        options['showUsage'] = True 
        options['message'] = 2 
        return options
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            options['showUsage'] = True 
            return options
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
    rest = []
    get_md5_files(files, bags, rest, [ Path(arg) for arg in args ], arg_dict, verbose)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if len(files) > 0:
        write_csv_file(files, stamp, verbose)
    if len(bags) > 0:
        write_file_list(bags, 'bag_paths', stamp, verbose)
    if len(rest) > 0:
        write_file_list(rest, 'rest_paths', stamp, verbose)
    return 0 

def write_file_list(bag: List[PosixPath], name: str, stamp: str, verbose: bool):
    """Write list of bag paths 
    """
    out = Path(f"{stamp}_{name}.txt")
    out.write_text("\n".join(str(p) for p in bag) + "\n", encoding="utf-8")
    if verbose:
        print(f"Geschrieben: {out}")

def write_csv_file(files: List[dict], stamp: str, verbose: bool):
    """Write md5 information for file to CSV file
    """
    out = Path(f"{stamp}_md5-mapping.csv")
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=files[0].keys())
        writer.writeheader()
        writer.writerows(files)
    if verbose:
        print(f"Geschrieben: {out}")

def detect_bom(path) ->str:
    with path.open("rb") as f:
        raw = f.read(4)
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    elif raw.startswith(b"\xff\xfe\x00\x00"):
        return "utf-32-le"
    elif raw.startswith(b"\x00\x00\xfe\xff"):
        return "utf-32-be"
    elif raw.startswith(b"\xff\xfe"):
        return "utf-16-le"
    elif raw.startswith(b"\xfe\xff"):
        return "utf-16-be"
    return None  # keine BOM gefunden

def find_md5_file(file_path: PosixPath) ->dict:
    """Try to find the corresponding md5 file for file_path
    """
    result = { 'file': file_path, 'md5file': None, 'md5': None, 'error': None }
    pattern = file_path.stem + "*md5*"
    result['md5file'] = next(file_path.parent.rglob(pattern), None)
    if result['md5file'] is not None and result['md5file'].is_file():
        encoding = detect_bom(result['md5file'])
        with open(result['md5file'], "r", encoding=encoding) as file:
            try:
                first_line = file.readline()
                if first_line:
                    m = MD5_PATTERN.match(first_line)
                    if m and m.groupdict()['hash'] is not None: 
                        result['md5'] = m.groupdict()['hash']    
            except Exception as e:
                print(f'Error reading file {result["md5file"]}: {e}')
                result['error'] = 'Error reading file'
    return result

def get_md5_files(files: List[dict], bags: List[PosixPath], rest: List[PosixPath], paths: List[PosixPath], options: dict, verbose: bool):
    """Get a list of files from input arguments
    """
    for file_path in paths:
        if file_path.is_dir() and not re.match('^.*s-([a-z0-9]{1,}-)*bag$', file_path.name):
            get_md5_files(files, bags, rest, list(file_path.glob('*')), options, verbose)
        elif re.match('^.*s-([a-z0-9]{1,}-)*bag$', file_path.name):
            bags.append(file_path)
        elif file_path.suffix in EXTENSIONS:
            result = find_md5_file(file_path)
            files.append(result)
            if verbose:
                print(f'{len(files)} files added ...', end='\r')
        elif file_path.suffix not in [ '.md5', '.txt']:
            rest.append(file_path)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

