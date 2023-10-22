#!/usr/bin/env python3.11

import argparse
import csv
import re
import sys
import zipfile


CSV_EXT_RX = re.compile(r'.*\.csv$')


# class Namespace(argparse.Namespace):
#     def __getattr__(self, name: str) -> str:
#         if name in self.__dict__:
#             return self.__dict__[name]
#         else:
#             return ''


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        sys.stderr.write('error: %s\n' % message)
        self.print_help())


def get_args(argv: List[str]) -> Tuple[Namespace, ArgumentParser]:
    parser = ArgumentParser(prog='Seekrits',
                            description = 'Secrets config file reader & writer')
    parser.add_argument('--file', '-f', dest='file', type=str, action='store')
    parser.add_argument('--limit', '-l', dest='max_csv_files', default=0, type=int, action='store', nargs='?')
    parser.add_argument('--max', '-m', dest='max_csv_rows', default=0, type=int, action='store', nargs='?')

#     parser.add_argument('--export', '-x', dest='export_file', type=str, action='store')
#     parser.add_argument('--section', '-s', dest='section', type=str, action='store', default='DEFAULT')
#     parser.add_argument('--key', '-k', dest='key', action='store', type=str)
#     parser.add_argument('--write', '-w', dest='write', action='store', type=str, nargs='?')
#     parser.add_argument('--use', '-u', dest='usage', action='store', const=1, nargs='?')
    return parser.parse_args(argv), parser


def haircut(zip_filename, max_files, max_rows):
    with zipfile.ZipFile(zip_filename, "r") as zip:
        files_done = 0
        for name in zip.namelist():
            if CSV_EXT_RX.matches(name):
                with zip.open(name) as file:
                    with csv.DictReader(io.TextIOWrapper(file, encoding='utf-8')) as csv_rdr:
                        rows_done = 0
                        for row in csv_rdr:
                            print(row)
                            if max_rows and (rows_done := rows_done + 1) > max_rows:
                                break
                        import pudb; pu.db
                        data = file.read().decode('utf-8')
                        print(f"{filename}.{name}({len(data)})....")
                    files_done += 1
                    if max_files and (files_done:= files_done + 1) > max_files:
                        break


def main(argv=None):
    if argv is None:
        argv = sys.argv
    args, parser = get_args(argv)
    if args.file:
        haircut(file, args.max_csv_files, args.max_csv_rows)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main(*sys.argv[1:])
    except Exception as ee:
        print(ee)
