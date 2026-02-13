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
from colorama import Fore, Style
import os
from pathlib import Path, PosixPath
import re

DEBUG = False 

class Result:
    """This class represents the result of the Mediastandard check
    """
    def __init__(self, check_passed=True, error_msg="", groups=None): 
        self.check_passed = check_passed
        self.error_msg = error_msg
        self.groups = groups

    def addMessage(self, message: str, m: re.Match):
        """Adds a error message
        """
        if len(m.groupdict()):
            self.groups = m.groupdict()
        if ":" in self.error_msg:
            self.error_msg = self.error_msg + " " + message
        else:
            self.error_msg = self.error_msg + ": " + message


    def getFilenameInfo(self, file_path: PosixPath, color='') ->str:
        """Get graphical information about filename
        """
        if file_path.exists():
            if not self.check_passed and self.groups:
                return color + f'{file_path.parent.absolute()}{os.sep}{self.groups["before"]}' + Fore.RED + f'{self.groups["error"]}' + Style.RESET_ALL + color + f'{self.groups["after"]}' + Style.RESET_ALL
            return file_path.absolute()
        else:
            if not self.check_passed and self.groups:
                return color + f'{self.groups["before"]}' + Fore.RED + f'{self.groups["error"]}' + Style.RESET_ALL + color + f'{self.groups["after"]}' + Style.RESET_ALL
            return file_path.name


