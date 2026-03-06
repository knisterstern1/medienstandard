#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This program can be used to check whether the filename of files accords with the mediastandard.
"""
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
from colorama import Fore, Style
from pathlib import Path, PosixPath
import sys

# my modules
from simple_mediastandard_validation import Printer, main, usage, get_filenames

DEBUG = False 

class FancyPrinter(Printer):
    """This class represents a fancy output printer.
    """
    def __init__(self):
        self.color_dict = { "default": Fore.LIGHTBLUE_EX, "comment": Fore.LIGHTWHITE_EX, "fail": Fore.RED, "highlight": Fore.MAGENTA, "reset": Style.RESET_ALL}
    def get_filename(self, file_path: PosixPath) ->str:
        return Fore.LIGHTBLUE_EX + str(file_path.absolute()) + Style.RESET_ALL if file_path.exists() else Fore.LIGHTBLUE_EX + file_path.name + Style.RESET_ALL

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], FancyPrinter()))

