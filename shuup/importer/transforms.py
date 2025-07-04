import codecs
import csv
import os

import openpyxl
import six
import xlrd
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _

from shuup.utils.excs import Problem


class RowYielder:
    def __init__(self, sheet_or_data):
        self.sheet_or_data = sheet_or_data

    def transform_values(self, row):
        return row


class XLSRowYielder(RowYielder):
    def __iter__(self):
        for y in range(self.sheet_or_data.nrows):
            yield self.transform_values(self.sheet_or_data.row_values(y))


class XLSXRowYielder(RowYielder):
    def __iter__(self):
        for row in self.sheet_or_data.rows:
            yield self.transform_values([(force_text(cell.value) if cell.value else None) for cell in row])


class TransformedData:
    def __init__(self, mode, headers, rows, **meta):
        self.mode = mode
        self.headers = headers
        self.meta = meta
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, key):
        return self.rows[key]

    def __len__(self):
        return len(self.rows)


def process_data(rows):
    headers = []
    got_data = set()
    data = []
    if not len(data):
        for y, row in enumerate(rows):
            if not any(row):  # Ignore any fully cleared rows
                continue
            if y == 0:
                headers = [x.lower().strip() for x in row if x]
                continue
            datum = dict(zip(headers, row))
            got_data.update({h for (h, d) in six.iteritems(datum) if d})
            data.append(datum)

    row_limit = getattr(settings, "IMPORT_MAX_ROWS", 1000)
    if len(data) > row_limit:
        raise Problem(_("Can't import more than %s rows from one file.") % row_limit)
    return (data, got_data)


def transform_file(mode, filename, data=None):
    meta = {}

    if mode == "xls":
        wb = xlrd.open_workbook(filename, file_contents=data, on_demand=True, formatting_info=True)
        sheet = wb.get_sheet(0)
        data, got_data = process_data(rows=XLSRowYielder(sheet))
        meta["xls_datemode"] = wb.datemode
    elif mode == "xlsx":
        wb = openpyxl.load_workbook(filename)
        sheet = wb.worksheets[0]
        data, got_data = process_data(rows=XLSXRowYielder(sheet))
    elif mode == "csv":
        # for python2 http://stackoverflow.com/questions/904041/reading-a-utf8-csv-file-with-python/14786752#14786752
        data, got_data = py3_read_file(data, filename)
    else:
        raise NotImplementedError(
            f"Error! Not implemented: `TransformedData` -> `transform_file()` -> mode `{mode}` is not implemented."
        )

    headers = data[0].keys() if len(data) else []
    clean_keys = set(headers) - got_data
    for datum in data:
        for key in clean_keys:
            datum.pop(key, None)

    return TransformedData(mode, headers, data, **meta)


def py2_read_file(data, filename):
    got_data = set()
    data = []
    with open(filename) as f:
        dialect = csv.Sniffer().sniff(f.read(20480))
        f.seek(0)
        for _x, row in enumerate(csv.DictReader(f, dialect=dialect)):
            got_data.update({h.lower() for (h, d) in six.iteritems(row) if d})
            data.append({k.lower(): v if v else None for k, v in six.iteritems(row)})
    return data, got_data


def py3_read_file(data, filename):
    got_data = set()
    data = []

    bytes = min(32, os.path.getsize(filename))
    raw = open(filename, "rb").read(bytes)

    if raw.startswith(codecs.BOM_UTF8):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"

    with open(filename, encoding=encoding) as f:
        dialect = csv.Sniffer().sniff(f.read(20480))
        f.seek(0)
        for _x, row in enumerate(csv.DictReader(f, dialect=dialect)):
            got_data.update({h.lower() for (h, d) in six.iteritems(row) if d})
            data.append({k.lower(): v if v else None for k, v in six.iteritems(row)})
    return data, got_data
