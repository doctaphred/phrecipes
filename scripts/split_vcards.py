#!/usr/bin/env python3 -u
"""Split a multi-vCard file into one file per vCard."""
import re


VCARD_EXTENSION = '.vcf'
VCARD_REGEX = re.compile(r'BEGIN:VCARD\n.*?\nEND:VCARD\n', flags=re.DOTALL)
FN_REGEX = re.compile('^FN:(.*?)$', flags=re.MULTILINE)


def unique_dest(name, ext):
    f = None
    while f is None:
        unique_name = name + ext
        try:
            f = open(unique_name, 'x')
        except FileExistsError:
            name = name + '_'
    return f


if __name__ == '__main__':
    import sys
    _, file_path = sys.argv

    with open(file_path) as f:
        data = f.read()

    cards = VCARD_REGEX.findall(data)
    for card in cards:
        name = FN_REGEX.search(card).group(1)
        with unique_dest(name, VCARD_EXTENSION) as f:
            print(f.name)
            f.write(card)
