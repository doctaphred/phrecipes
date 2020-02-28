#!/usr/bin/env python3
"""Update a database table with a CSV."""
import csv
import sys
from pathlib import Path

import dataset
from tqdm import tqdm


def chunks(it, chunk_size):
    """Yield lists of <chunk_size> elements of <it>."""
    assert chunk_size > 0
    it = iter(it)
    while True:
        chunk = [i for _, i in zip(range(chunk_size), it)]
        if chunk:  # Don't yield an empty chunk if len(it) % chunk_size == 0.
            yield chunk
        if len(chunk) != chunk_size:
            break  # Must have been the last chunk.


def count_lines(f):
    """Count the number of lines in the open file."""
    start = f.tell()
    try:
        return sum(1 for _ in f)
    finally:
        f.seek(start)


def read_lines(path):
    """Open <path> and read lines."""
    with open(path) as f:
        yield from f


def read_lines_with_progress(path):
    """Open <path> and read lines with a progress bar."""
    with open(path) as f:
        yield from tqdm(f, total=count_lines(f))


def csv_rows(lines, headers=None, **csv_reader_kwargs):
    """Parse lines of CSV data into dicts."""
    reader = csv.reader(lines, **csv_reader_kwargs)
    if headers is None:
        headers = next(reader)
    for row in reader:
        assert len(row) == len(headers)
        # This is substantially faster than csv.DictReader, which
        # constructs OrderedDicts.
        yield dict(zip(headers, row))


def insert_chunks(table, rows, chunk_size=1000):
    """Insert <rows> into <table>, <chunk_size> at a time."""
    for chunk in chunks(rows, chunk_size=chunk_size):
        table.insert_many(chunk, chunk_size=chunk_size)


def with_file_data(filename, rows):
    """Add the filename and line number to each row."""
    for i, row in enumerate(rows, start=2):
        assert 'filename' not in row
        assert 'lineno' not in row
        row['filename'] = filename
        row['lineno'] = i
        yield row


def csv_to_db(db_url, csv_path, table_name):

    # TODO: make (filename, row) the primary key?

    # TODO: create separate table for filenames?

    # TODO: timestamp rows/files?

    # TODO: zipfile support.

    db = dataset.connect(db_url)
    table = db[table_name]

    lines = read_lines_with_progress(csv_path)
    rows = with_file_data(
        filename=Path(csv_path).name,
        rows=csv_rows(lines, delimiter='|'),
    )

    insert_chunks(table, rows)


if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__)
        raise SystemExit(0)

    try:
        _, db_url, csv_path, table_name = sys.argv
    except ValueError:
        print(f"Usage: {__file__} <db_url> <csv_path> <table_name>")
        raise SystemExit(1)

    csv_to_db(db_url, csv_path, table_name)
