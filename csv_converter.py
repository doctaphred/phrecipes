import csv
from ast import literal_eval
from csv import DictReader


def csv_data(filepath, **conversions):
    """Yield rows from the CSV file as dicts, with column headers as the keys.

    Values in the CSV rows are converted to Python values when possible,
    and are kept as strings otherwise.

    Specific conversion functions for columns may be specified via
    `conversions`: if a column's header is a key in this dict, its value
    will be applied as a function to the CSV data. For example, specify
    `ColumnHeader=str` if all values in the column should be interpreted
    as unquoted strings, but might be valid Python literals (`True`,
    `None`, `1`, etc.).

    Example usage:

    >>> csv_data(filepath,
    ...          VariousWordsIncludingTrueAndFalse=str,
    ...          NumbersOfVaryingPrecision=float,
    ...          FloatsThatShouldBeRounded=round,
    ...          BuiltInNames=lambda name: getattr(__builtins__, name),
    ...          **{'Column Header With Spaces': arbitrary_function})
    """

    def convert(key, value):
        try:
            conversion = conversions[key]
        except KeyError:
            pass
        else:
            return conversion(value)

        try:
            # Interpret the string as a Python literal
            return literal_eval(value)
        except (SyntaxError, TypeError, ValueError):
            pass

        # If nothing else worked, assume it's an unquoted string
        return value

    with open(filepath) as f:
        # QUOTE_NONE: don't process quote characters, to avoid the value
        # `"2"` becoming the int `2`, rather than the string `'2'`.
        for row in DictReader(f, quoting=csv.QUOTE_NONE):
            yield {k: convert(k, v) for k, v in row.items()}
        # TODO: consider eager or partially-eager approaches to avoid
        # excessive disk calls:
        # return [{k: convert(k, v) for k, v in row.items()}
        #         for row in DictReader(f, quoting=csv.QUOTE_NONE)]
