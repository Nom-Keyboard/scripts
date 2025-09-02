#!/usr/bin/env python
import argparse
import csv
import io
import sys
import typing

HEX_CODE_POINT = 'hexadecimal codepoint'

class StringJoinAction(argparse.Action):
  def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: list[str], option_string: typing.Optional[str] = None):
    setattr(namespace, self.dest, ''.join(values))

ap = argparse.ArgumentParser(description='tool for inserting new entries into a dictionary', epilog='example: %(prog)s -f vietnamese.tsv -c 21a38 5583 -w "chữ Nôm"')
ap.register('type', HEX_CODE_POINT, lambda s: chr(int(s, 16)))
ap.add_argument('-f', '--csv_file', required=True, type=argparse.FileType('ab+'), help='path to the dictionary file to operate on, an empty one is created automatically if not pre-existing')
ap.add_argument('-c', '--code_point', type=HEX_CODE_POINT, nargs='*', action=StringJoinAction, help='raw hexadecimal value expressing the unicode character for the nôm representation. if not provided, a search is performed with the given word and the code point values will be dumped')
ap.add_argument('-w', '--word', required=True, help='standard representation of the word to be added')
args = ap.parse_args()

(fd := io.TextIOWrapper(getattr(args, 'csv_file'), newline='', encoding='utf-8')).seek(0)

search_found = False

for nom_representation, standard_representation in csv.reader(fd, dialect=csv.excel_tab):
  if args.code_point is None:
    if standard_representation == args.word:
      print(f'{nom_representation}\t{" ".join(f"{ord(c):x}" for c in nom_representation)}')
      search_found = True
  elif nom_representation == args.code_point and standard_representation == args.word:
    print('One identical entry already exists, Stop.', file=sys.stderr)
    sys.exit(1)

if args.code_point is None:
  if not search_found:
    print('No matching word found.', file=sys.stderr)
    sys.exit(1)
else:
  csv.writer(fd, dialect=csv.excel_tab).writerow([args.code_point, args.word])
  print('Successfully added 1 entry.', file=sys.stderr)
