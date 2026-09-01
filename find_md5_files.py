#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This program can be used to find all md5 checksum files in a folder and print a CSV mapping file.
"""
# Copyright (C) Christian Steiner 2025 {{{1
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/> 1}}}

from collections import defaultdict
from datetime import datetime
import csv
import getopt
import os
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Tuple

EXTENSIONS = {'.mkv', '.mov', '.mp4', '.tif', '.jpg', '.iso', '.pdf'}

# Endungen, die weder als Medien- noch als Restdatei gemeldet werden
IGNORED_EXTENSIONS = {'.md5', '.txt'}

MD5_PATTERN = re.compile(
    r"^(?:(?P<prefix>.*?)\s+)?"       # optionaler Praefix-Text + Whitespace
    r"(?P<hash>[a-fA-F0-9]{32})"      # der MD5-Hash
    r"(?![a-fA-F0-9])"                # kein weiteres Hex-Zeichen (schuetzt vor SHA)
    r"(?:\s+[*]?(?P<filename>.+))?$"  # optionaler Dateiname, evtl. mit Binaermarker
)

# BSD-Stil: MD5 (Datei.tif) = <hash>
MD5_BSD_PATTERN = re.compile(
    r"^\s*MD5\s*\(\s*(?P<filename>.+?)\s*\)\s*=\s*(?P<hash>[a-fA-F0-9]{32})\s*$",
    re.IGNORECASE
)

BAG_PATTERN = re.compile(r'^.*[_-]bag$', re.IGNORECASE)

# Erkennt md5-Dateien anhand ihres Namens
MD5_FILE_PATTERN = re.compile(r'md5', re.IGNORECASE)

# Marker, die beim Ableiten des Bezugsnamens entfernt werden
MD5_MARKER_PATTERN = re.compile(r'[._\-\s]*md5[._\-\s]*', re.IGNORECASE)

FIELDNAMES = ['file', 'md5file', 'md5', 'md5_filename', 'status', 'note']

# Statuswerte fuer die Spalte 'status'
ST_OK          = 'ok'                # Hash gefunden und zugeordnet
ST_KEIN_MD5    = 'kein_md5'          # keine passende md5-Datei vorhanden
ST_MEHRDEUTIG  = 'mehrdeutig'        # mehrere md5-Dateien kommen in Frage
ST_NICHT_PARS  = 'nicht_parsbar'     # md5-Datei vorhanden, kein Hash erkennbar
ST_LESEFEHLER  = 'lesefehler'        # md5-Datei nicht lesbar
ST_NAME_ABW    = 'name_abweichung'   # Hash gefunden, notierter Name passt nicht
ST_ENCODING    = 'encoding_unsicher' # Datei nur mit Ersatzzeichen lesbar


def parse_options(argv: List[str]) -> dict:
    """
    OPTIONS:
        -h|--help           show help
        -p|--output-prefix  prefix for output files
        -v|--verbose        print information
        -o|--outdir DIR     write output files to DIR (default: current directory)
    """
    options = {'args': [], 'verbose': False, 'outdir': Path('.'), 'outputPrefix': '',
               'showUsage': False, 'message': 0}
    try:
        opts, args = getopt.getopt(argv, "hvp:o:", ["help", "verbose", "output-prefix=", "outdir="])
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
        elif opt in ('-p', '--output-prefix'):
            options['outputPrefix'] = arg
        elif opt in ('-o', '--outdir'):
            options['outdir'] = Path(arg)
    options['args'] = args
    if not args:
        options['showUsage'] = True
        options['message'] = 2
    return options


def usage() -> int:
    """prints information on how to use the script
    """
    print("\n\t" + sys.argv[0] + " [OPTIONS] file1 file2 ... | directory")
    print(parse_options.__doc__)
    print("\t:return: exit code (int)")
    return 0


def detect_bom(path: Path) -> Optional[str]:
    """Detect encoding from a byte order mark, return None if there is none.
    """
    try:
        with path.open("rb") as f:
            raw = f.read(4)
    except OSError:
        return None
    # Die -sig / endianlosen Codecs entfernen die BOM beim Dekodieren; die
    # expliziten Varianten (utf-16-le usw.) wuerden sie als \ufeff im Text
    # stehen lassen und die erste Zeile unbrauchbar machen.
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    elif raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
        return "utf-32"
    elif raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return "utf-16"
    return None


def read_text_robust(path: Path) -> Tuple[Optional[str], bool]:
    """Read a text file. Returns (text, unsicher).

    Ohne BOM wird utf-8 erzwungen statt der Locale-Vorgabe, damit das Ergebnis
    auf jedem Rechner identisch ausfaellt. Schlaegt utf-8 fehl, wird cp1252
    versucht und das Ergebnis als unsicher markiert.
    """
    encoding = detect_bom(path)
    if encoding is not None:
        return path.read_text(encoding=encoding), False
    try:
        return path.read_text(encoding='utf-8'), False
    except UnicodeDecodeError:
        return path.read_text(encoding='cp1252', errors='replace'), True


def reference_name(md5_path: Path) -> str:
    """Leitet aus dem Namen einer md5-Datei den Namen der Bezugsdatei ab.

    Beispiele:
        Bild_001.md5          -> bild_001
        Bild_001.tif.md5      -> bild_001.tif
        Bild_001_md5.txt      -> bild_001
        md5_Bild_001.txt      -> bild_001
    """
    name = md5_path.name.lower()
    for suffix in ('.md5', '.txt'):
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    name = MD5_MARKER_PATTERN.sub('', name)
    return name.strip('._- ')


def collect(paths: List[Path],
            media: List[Path],
            md5_index: Dict[Path, List[Path]],
            bags: List[Path],
            rest: List[Path],
            seen: set,
            verbose: bool):
    """Einmaliger Durchlauf: klassifiziert alle Eintraege und baut nebenbei
    den Index der md5-Dateien je Verzeichnis auf.
    """
    for path in paths:
        try:
            is_dir = path.is_dir()
        except OSError as e:
            rest.append(path)
            print(f'Warnung: {path} nicht zugreifbar: {e}', file=sys.stderr)
            continue

        if is_dir:
            if BAG_PATTERN.match(path.name):
                bags.append(path)
                continue
            # Schutz gegen Symlinks und Junctions
            try:
                real = path.resolve()
            except OSError:
                real = path
            if real in seen:
                print(f'Warnung: Schleife uebersprungen: {path}', file=sys.stderr)
                continue
            seen.add(real)
            try:
                kinder = sorted(path.iterdir())
            except OSError as e:
                print(f'Warnung: {path} nicht lesbar: {e}', file=sys.stderr)
                continue
            collect(kinder, media, md5_index, bags, rest, seen, verbose)
            continue

        suffix = path.suffix.lower()
        if MD5_FILE_PATTERN.search(path.name) and suffix in IGNORED_EXTENSIONS:
            md5_index[path.parent].append(path)
        elif suffix in EXTENSIONS:
            media.append(path)
            if verbose:
                print(f'{len(media)} files added ...', end='\r')
        elif suffix not in IGNORED_EXTENSIONS:
            rest.append(path)


def parse_md5_entries(text: str) -> List[Tuple[str, Optional[str]]]:
    """Liefert alle (hash, dateiname) Paare aus dem Text einer md5-Datei.
    """
    entries = []
    for line in text.lstrip('\ufeff').splitlines():
        line = line.strip().lstrip('\ufeff')
        if not line:
            continue
        m = MD5_BSD_PATTERN.match(line) or MD5_PATTERN.match(line)
        if m and m.group('hash'):
            name = m.group('filename')
            entries.append((m.group('hash').lower(), name.strip() if name else None))
    return entries


def find_md5_file(file_path: Path, md5_index: Dict[Path, List[Path]]) -> dict:
    """Ordnet file_path die passende md5-Datei zu und liest den Hash aus.
    """
    result = {'file': file_path, 'md5file': None, 'md5': None,
              'md5_filename': None, 'status': ST_KEIN_MD5, 'note': None}

    ziele = {file_path.name.lower(), file_path.stem.lower()}
    kandidaten = [p for p in md5_index.get(file_path.parent, [])
                  if reference_name(p) in ziele]

    if not kandidaten:
        return result

    if len(kandidaten) > 1:
        result['status'] = ST_MEHRDEUTIG
        result['note'] = ' | '.join(sorted(p.name for p in kandidaten))
        return result

    md5_path = kandidaten[0]
    result['md5file'] = md5_path

    try:
        text, unsicher = read_text_robust(md5_path)
    except OSError as e:
        result['status'] = ST_LESEFEHLER
        result['note'] = str(e).replace('\n', ' ')
        return result
    except Exception as e:
        result['status'] = ST_LESEFEHLER
        result['note'] = f'{type(e).__name__}: {e}'.replace('\n', ' ')
        return result

    entries = parse_md5_entries(text)
    if not entries:
        result['status'] = ST_NICHT_PARS
        result['note'] = 'kein 32-stelliger Hash gefunden'
        return result

    # Bei mehreren Eintraegen den zum Dateinamen passenden waehlen
    treffer = [e for e in entries
               if e[1] and Path(e[1].replace('\\', '/')).name.lower() == file_path.name.lower()]
    if treffer:
        gewaehlt = treffer[0]
    elif len(entries) == 1:
        gewaehlt = entries[0]
    else:
        result['status'] = ST_MEHRDEUTIG
        result['note'] = f'{len(entries)} Hash-Zeilen, keine passt zum Dateinamen'
        return result

    result['md5'] = gewaehlt[0]
    result['md5_filename'] = gewaehlt[1]
    result['status'] = ST_OK

    if unsicher:
        result['status'] = ST_ENCODING
        result['note'] = 'kein BOM, utf-8 fehlgeschlagen, cp1252 mit Ersatzzeichen'
    elif gewaehlt[1] and Path(gewaehlt[1].replace('\\', '/')).name.lower() != file_path.name.lower():
        result['status'] = ST_NAME_ABW
        result['note'] = 'notierter Dateiname weicht ab'

    return result


def write_csv_file(files: List[dict], outputPrefix: str, outdir: Path, stamp: str, verbose: bool):
    """Write md5 information for file to CSV file
    """
    prefix = f"{outputPrefix}_" if outputPrefix != '' else ''
    out = outdir / f"{stamp}_{prefix}md5-mapping.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=';',
                                extrasaction='ignore')
        writer.writeheader()
        for row in files:
            writer.writerow({k: ('' if row.get(k) is None else str(row.get(k)))
                             for k in FIELDNAMES})
    if verbose:
        print(f"Geschrieben: {out}")


def write_file_list(paths: List[Path], outputPrefix: str, name: str, outdir: Path, stamp: str, verbose: bool):
    """Write list of paths
    """
    prefix = f"{outputPrefix}_" if outputPrefix != '' else ''
    out = outdir / f"{stamp}_{prefix}{name}.txt"
    out.write_text("\n".join(str(p) for p in paths) + "\n", encoding="utf-8")
    if verbose:
        print(f"Geschrieben: {out}")


def main(argv: List[str]):
    """This program can be used to find all md5 checksum files in a folder and print a CSV mapping file."""
    arg_dict = parse_options(argv)
    if arg_dict['showUsage']:
        usage()
        return arg_dict['message']

    verbose = arg_dict['verbose']
    outdir = arg_dict['outdir']
    outdir.mkdir(parents=True, exist_ok=True)
    if arg_dict['outputPrefix'] == '' and len(arg_dict['args']) == 1:
        arg_dict['outputPrefix'] = Path(arg_dict['args'][0]).name

    media: List[Path] = []
    md5_index: Dict[Path, List[Path]] = defaultdict(list)
    bags: List[Path] = []
    rest: List[Path] = []

    collect([Path(arg) for arg in arg_dict['args']],
            media, md5_index, bags, rest, set(), verbose)

    if verbose:
        anzahl_md5 = sum(len(v) for v in md5_index.values())
        print(f'\n{len(media)} Mediendateien, {anzahl_md5} md5-Dateien, '
              f'{len(bags)} Bags, {len(rest)} sonstige Dateien.')

    files = [find_md5_file(p, md5_index) for p in media]

    # md5-Dateien, die keiner Mediendatei zugeordnet werden konnten
    zugeordnet = {r['md5file'] for r in files if r['md5file'] is not None}
    verwaist = [p for liste in md5_index.values() for p in liste
                if p not in zugeordnet]

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if files:
        write_csv_file(files, arg_dict['outputPrefix'], outdir, stamp, verbose)
    if bags:
        write_file_list(bags, arg_dict['outputPrefix'], 'bag_paths', outdir, stamp, verbose)
    if rest:
        write_file_list(rest, arg_dict['outputPrefix'],  'rest_paths', outdir, stamp, verbose)
    if verwaist:
        write_file_list(sorted(verwaist), arg_dict['outputPrefix'], 'md5_ohne_bezug', outdir, stamp, verbose)

    # Zusammenfassung nach Status
    zaehler: Dict[str, int] = defaultdict(int)
    for r in files:
        zaehler[r['status']] += 1
    print('')
    for status in (ST_OK, ST_NAME_ABW, ST_ENCODING, ST_KEIN_MD5,
                   ST_MEHRDEUTIG, ST_NICHT_PARS, ST_LESEFEHLER):
        if zaehler[status]:
            print(f'  {status:<18} {zaehler[status]:>7}')
    if verwaist:
        print(f'  {"md5_ohne_bezug":<18} {len(verwaist):>7}')

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
