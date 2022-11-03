#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
import base64
import getpass
import os
import sys
from typing import List, Tuple

from configparser_crypt import ConfigParserCrypt


USAGE_NOTES = """
NOTE: in all cases where --file exists on filesystem, the script expects a
32-byte AES passphrase that is encoded with the base64.standard_b64encode charset.

For a new --file, a random key is generated and sent to /dev/stdout

Common use patterns:

# Import a plaintext config file to a new encrypted config file
% seekrits.py --import <myconfig.conf> --file <mysecrets.conf.enc>

# Set or change a key-value pair, in a SECTION of a new or existing encrypted config file 
% seekrits.py --file <mysecrets.conf.enc> -s <SECTION> -k <config_key> -w <new_value>

# Read a key's value, from a SECTION, of an existing encrypted config file, output to console
% seekrits.py --file <mysecrets.conf.enc> -s <SECTION> -k <config_key>

# Export an encrypted config file to a plaintext file, or /dev/std[out|err]
% seekrits.py --file <mysecrets.conf.enc> --export /dev/stdout
"""


def get_args(argv: List[str]) -> Tuple[Namespace, ArgumentParser]:
    parser = ArgumentParser(prog='Seekrits',
                            description = 'Secrets config file reader & writer')
    parser.add_argument('--file', '-f', dest='file', type=str, action='store')
    parser.add_argument('--import', '-i', dest='import_file', type=str, action='store')
    parser.add_argument('--export', '-x', dest='export_file', type=str, action='store')
    parser.add_argument('--section', '-s', dest='section', type=str, action='store', default='DEFAULT')
    parser.add_argument('--key', '-k', dest='key', action='store', type=str)
    parser.add_argument('--write', '-w', dest='write', action='store', type=str, nargs='?')
    parser.add_argument('--use', '-u', dest='usage', action='store', const=1, nargs='?')
    return parser.parse_args(argv), parser


def read_section_key(conf: ConfigParserCrypt, key: str):
    return conf


def get_config(source_file) -> ConfigParserCrypt:
    config = ConfigParserCrypt()
    passphrase = None
    if not os.path.isfile(source_file):
        passphrase = config.generate_key()
        print(f"Passphrase for new config file: '{base64.standard_b64encode(passphrase)}'.  "
              "Copy the passphrase, then use 'reset' to clear the terminal.")
        config.aes_key = passphrase

    if not passphrase:
        if sys.stdin.isatty():
            # If script is executing in a terminal, display a user prompt
            passph = getpass.getpass("Passphrase: ")
            passphrase = base64.standard_b64decode(passph)
        else:
            # Otherwise, script is running in a pipe, tf no user prompt
            passph = sys.stdin.readline().rstrip()
            passphrase = base64.standard_b64decode(passph)
        config.aes_key = passphrase

    if os.path.isfile(source_file):
        config.read_encrypted(source_file)

    return config


def write_key_value(config, file, section, key, value):
    if section not in config:
        config.add_section(section)
    config[section][key] = value
    with open(file, "wb") as fp:
        config.write_encrypted(fp, space_around_delimiters=False)
    if not os.path.isfile(file) or not os.path.getsize(file):
        print(f"Problem writing config file {file}, dumping")
        with open("/dev/stdout", "w") as fp:
            print(config.write(fp, space_around_delimiters=False))


def read_key_value(config, file, section, key):
    config.read_encrypted(file)
    if section not in config:
        raise ValueError(f"Could not find section '{section}' in file '{file}'")
    if key not in config[section]:
        raise ValueError(f"Could not find key '{key}' in section '{section}' in file '{file}'")
    print(config[section][key])


def encrypt_config_file(import_file, output_file):
    source = ConfigParserCrypt()
    dest = get_config(output_file)

    with open(import_file, "r") as fh:
        source.read_string("[DEFAULT]\n" + fh.read())

    sections = 0
    key_values = 0
    for section in source:
        if section not in dest:
            dest.add_section(section)
            sections += 1
        for key in source[section]:
            dest[section][key] = source[section][key]
            key_values += 1

    with open(output_file, "wb") as fp:
        dest.write_encrypted(fp)

    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"Transfered {sections} sections and {key_values} key-value pairs.")


def decrypt_config_file(source_file, export_file):
    source = get_config(source_file)
    with open(export_file, "w") as fp:
        source.write(fp, space_around_delimiters=False)


def main(argv):
    args, parser = get_args(argv)
    if args.usage or len(argv) < 4:
        parser.print_help()
        sys.stderr.write(USAGE_NOTES)
        exit(1)

    if args.import_file and args.file:
        if args.import_file == args.file:
            raise ValueError(f"Import and output filenames cannot be the same!")
        elif not(os.path.exists(args.import_file) and not os.path.exists(args.file)):
            raise ValueError(f"Import file must exist, and output file must not exist!")
        encrypt_config_file(args.import_file, args.file)

    if args.file and args.export_file:
        if args.file == args.export_file:
            raise ValueError(f"Source and export filenames cannot be the same!")
        elif not(os.path.exists(args.file) and (args.export_file.startswith("/dev/") or not os.path.exists(args.export_file))):
            raise ValueError(f"Source file must exist, and export file must not exist!")
        decrypt_config_file(args.file, args.export_file)
    else:
        config = get_config(args.file)
        section = args.section if args.section else 'DEFAULT'
        if not args.file:
            raise ValueError("Required parameter missing: --file (-f)")
        if args.key:
            if args.write:
                write_key_value(config, args.file, section, args.key, args.write)
            else:
                read_key_value(config, args.file, section, args.key)
        else:
            raise ValueError("Required parameter missing: --key (-k)")


if __name__ == "__main__":
    main(sys.argv[1:])
