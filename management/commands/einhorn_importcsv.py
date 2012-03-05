#!/usr/bin/python

import datetime
import csv
from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from comic.models import Series, Category, DailyEntry


def csv_into_entry(datafile, is_dry=True, **kwargs):
    f = csv.reader(open(datafile), **kwargs)
    header = f.next()
    column = {}
    for i, x in enumerate(header):
        column[x.lstrip('#').rstrip('*[]')] = i
    for row in f:
        if len(row) == 0 or len(row[0]) == 0 or row[0][0] == '#': continue
        series = Series.objects.get(code=row[column["series"]])
        date = datetime.date(*(int(i) for i in row[column["date"]].split("-")))
        try:
            cats = [Category.objects.get(code=i.strip()) for i in row[column["category"]].split(",")]
        except ObjectDoesNotExist:
            print row[column["category"]].split(",")
            raise
        print date, cats
        d = DailyEntry(series=series,
                       date=date,
                       title_ja=row[column["title_ja"]],
                       title_en=row[column["title_en"]],
                       body_ja=row[column["body_ja"]],
                       body_en=row[column["body_en"]])
        if not is_dry:
            d.save()
            d.categories = cats

class Command(BaseCommand):
    help = 'Import data from old canal format to daily comic entry'
    args = "csvfile [csvfile..]"
    option_list = BaseCommand.option_list + (
        make_option('--delimiter', action='store', dest='delimiter',
                    default=',', help="CSV delimiter character."),
        make_option('--quotechar', action='store', dest='quotechar',
                    default='"', help="CSV quotation character."),
        make_option('-n', '--dry-run', action='store_true', dest='dry',
                    default=False, help="Only print data without importing."),
        )

    def handle(self, *csv_labels, **option):
        is_dry = option.get('dry')
        delimiter = option.get('delimiter')
        quotechar = option.get('quotechar')
        for i in csv_labels:
            print i
            csv_into_entry(i, delimiter=delimiter, quotechar=quotechar, is_dry=is_dry)
