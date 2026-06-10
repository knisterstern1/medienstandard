#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This program validates filenames from a CSV directory listing against the mediastandard."""

import csv
import getopt
import sys
from datetime import datetime
from pathlib import Path, PosixPath
from typing import List

# my modules
from mediastandard import MediaStandard
from simple_mediastandard_validation import Printer

DEBUG = False


def parse_options(argv: List[str]) -> dict:
    """

    OPTIONS:
        -c|--column=name    CSV column containing filenames (default: Name)
        -f|--fail-only      show only fails in terminal output
        -h|--help           show help
        -j|--json=file      mediastandard json file
        -p|--pattern        print regex pattern for mediastandard and exit
        -v|--verbose        print file information in terminal output

    """
    options = {
        "args": [],
        "column": "Name",
        "json": "medienstandard_v3-1_2026_regex.json",
        "verbose": False,
        "failOnly": False,
        "patternOnly": False,
        "showUsage": False,
        "message": 0,
    }
    try:
        opts, args = getopt.getopt(
            argv,
            "c:fhj:pv",
            ["column=", "fail-only", "help", "json=", "pattern", "verbose"],
        )
    except getopt.GetoptError:
        options["showUsage"] = True
        options["message"] = 2
        return options
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            options["showUsage"] = True
            return options
        elif opt in ("-c", "--column"):
            options["column"] = arg
        elif opt in ("-f", "--fail-only"):
            options["failOnly"] = True
        elif opt in ("-v", "--verbose"):
            options["verbose"] = True
        elif opt in ("-p", "--pattern"):
            options["patternOnly"] = True
        elif opt in ("-j", "--json"):
            options["json"] = arg
    options["args"] = args
    return options


def usage() -> int:
    print(main.__doc__)
    print("\n\t" + sys.argv[0] + " [OPTIONS] listing.csv")
    print(parse_options.__doc__)
    print("\t:return: exit code (int)")
    return 0


def detect_encoding(path: Path) -> str:
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
    return "utf-8"


def validate(printer: Printer, arg_dict: dict) -> int:
    args = arg_dict["args"]
    column = arg_dict["column"]
    json_file = arg_dict["json"]
    verbose = arg_dict["verbose"]
    fail_only = arg_dict["failOnly"]
    pattern_only = arg_dict["patternOnly"]

    checker = MediaStandard()
    if checker.load(json_file) != 0:
        print(f"Error: could not load {json_file}", file=sys.stderr)
        return 1
    printer.print_default(
        f"Medienstandard Version {checker.version}, {checker.year} geladen ..."
    )
    if verbose or pattern_only:
        printer.print_default(f"[Quelldatei: {json_file}]")
    if pattern_only:
        checker.display_rules_pattern()
        return 0

    if not args:
        return usage()

    csv_path = Path(args[0])
    if not csv_path.is_file():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        return 1

    encoding = detect_encoding(csv_path)
    with csv_path.open(encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            print(
                f"Error: column '{column}' not found. Available: {reader.fieldnames}",
                file=sys.stderr,
            )
            return 1
        rows = list(reader)
        original_fieldnames = list(reader.fieldnames)

    printer.print_highlight(
        f"Checking {len(rows)} filename{'s' if len(rows) != 1 else ''} from {csv_path.name} ..."
    )

    out_rows = []
    passed = 0
    failed = 0

    for row in rows:
        name = row[column]
        file_path = Path(name)
        result = checker.check_filename(file_path)

        if not result.check_passed:
            status = "FAIL"
            error = result.error_msg
            failed += 1
            filename_display = result.getFilenameInfo(printer.color_dict)
            printer.print_fail(filename_display, error, verbose)
        else:
            status = "OK"
            error = ""
            passed += 1
            try:
                information = checker.get_content(result)
                if not fail_only:
                    printer.print_information(name, information, verbose)
            except Exception as e:
                status = "FAIL"
                error = str(e)
                failed += 1
                passed -= 1
                printer.print_fail(name, error, verbose)

        out_row = dict(row)
        out_row["Status"] = status
        out_row["Error"] = error
        out_row["Standard"] = (
            f"{Path(json_file).stem} v{checker.version} ({checker.year})"
        )
        out_rows.append(out_row)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = csv_path.parent / f"{stamp}_{csv_path.stem}_validated.csv"
    out_fieldnames = original_fieldnames + ["Status", "Error", "Standard"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    printer.print_highlight(
        f"Summary: {passed} OK, {failed} FAIL — result written to {out_path.name}"
    )
    return 0 if failed == 0 else 1


def main(argv: List[str], printer: Printer):
    """Validates filenames in a CSV directory listing against the mediastandard."""
    arg_dict = parse_options(argv)
    if arg_dict["showUsage"]:
        usage()
        return arg_dict["message"]
    return validate(printer, arg_dict)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], Printer()))
