#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
import base64
import getpass
import os
import sys
from typing import List

from configparser_crypt import ConfigParserCrypt


def get_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser(prog='Seekrits',
                            description = 'Secrets reader & writer')
    parser.add_argument('--file', '-f', dest='file', type=str, action='store')
    parser.add_argument('--section', '-s', dest='section', type=str, action='store', default='DEFAULT')
    parser.add_argument('--key', '-k', dest='key', action='store', type=str)
    parser.add_argument('--write', '-w', dest='write', action='store', type=str, nargs='?')
    return parser.parse_args(argv)


def read_section_key(conf: ConfigParserCrypt, key: str):
    return conf


def get_config(args: Namespace) -> ConfigParserCrypt:
    config = ConfigParserCrypt()
    passphrase = None
    if not os.path.isfile(args.file):
        passphrase = config.generate_key()
        print(f"Passphrase for new config file: '{base64.standard_b64encode(passphrase)}'.  "
              "Copy the passphrase, then use 'reset' to clear the terminal.")
        config.aes_key = passphrase

    if not passphrase:
        if sys.stdin.isatty():
            passph = getpass.getpass("Passphrase: ")
            passphrase = base64.standard_b64decode(passph)
        else:
            passph = sys.stdin.readline().rstrip()
            passphrase = base64.standard_b64decode(passph)
        config.aes_key = passphrase

    if os.path.isfile(args.file):
        config.read_encrypted(args.file)

    return config


def write_key_value(config, file, section, key, value):
    if section not in config:
        config.add_section(section)
    config[section][key] = value
    # print(f"{section}.{args.key} set.")
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


def main(argv):
    args = get_args(argv)
    config = get_config(args)
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
