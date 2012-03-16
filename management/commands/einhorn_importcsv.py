#!/usr/bin/python

import os
import re
import csv
import sys
from optparse import make_option
from ConfigParser import SafeConfigParser
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import django_traindb.models

DEBUG = True
# DEBUG = False


"""
Generic CSV file importer.
Give the config file or guess field name from CSV header.
"""


def get_model_class(model_name_string):
    return getattr(globals()['django_traindb'].models,
                   model_name_string)


class get_object_with_field(object):
    def __init__(self, name, field):
        self.name = name
        self.field = field

    def __call__(self, x):
        name, field = self.name, self.field
        return get_model_class(name).objects.get(**{field: x})


class CSVConfigManager(object):

    """CSV loading configuration manager which can import csv data."""

    def __init__(self, configfile, model=None):
        if configfile is None:
            assert model is not None
            self.configparser = None
            if isinstance(model, models.Model):
                self.model = model
            else:
                self.model = get_model_class(model)
        else:
            if not os.path.isfile(configfile):
                raise IOError('config file not found: %s' % configfile)
            parser = SafeConfigParser()
            parser.read(configfile)
            self.modelstring = parser.sections()[0]
            self.model = get_model_class(self.modelstring)
            self.configparser = parser

    def set_header(self, header):
        self.column = [x for x in header]
        self.field = [None] * len(self.column)
        self.conv = [None] * len(self.column)
        self.referred = {}
        for i, label in enumerate(self.column):
            if (self.configparser is None
                or not self.configparser.has_option(self.modelstring, label)):
                self.field[i] = label
                self.conv[i] = lambda x: x
                continue
            setting = self.configparser.get(self.modelstring, label).split('=', 1)
            M = re.compile(r'([^[]+)(?:\[(.+?)\])?').match(setting[0])
            assert M, "type of label '%(field)s' is invalid: %(setting)s" % {
                    "field": label,
                    "setting": setting[0],
                    }
            command, target = M.groups()
            if command == "ignore":
                if DEBUG: print "%d '%s': ignore" % (i, label)
                self.field[i] = None
                self.conv[i] = lambda x: None
            elif command == "field":
                if DEBUG: print "%d '%s': field[%s]" % (i, label, target),
                self.field[i] = target
                if len(setting) == 1:
                    if DEBUG: print "pass"
                    self.conv[i] = lambda x: x
                    continue
                N = re.compile(r'([^(]+)(?:\((.+?)\))').match(setting[1])
                assert N, "option of label '%(field)s' is invalid: %(setting)s" % {
                    "field": label,
                    "setting": setting[1],
                    }
                convcommand, convarg = N.groups()
                if convcommand == "refer":
                    if DEBUG: print "refer", convarg
                    self.referred[label] = convarg
                    ref_name, ref_field = convarg.split('.')
                    ref_model = get_model_class(ref_name)
                    # lookup convarg with x
                    self.conv[i] = get_object_with_field(ref_name, ref_field)
                elif convcommand == "eval":
                    if DEBUG: print "eval", convarg
                    self.conv[i] = eval(convarg)
                else:
                    assert False, "incorrect: " + setting[1]
            else:
                assert False, "incorrect: " + setting[0]
        pass

    def get_field_name(self, column):
        return self.field[column]

    def get_field_value(self, column, string):
        try:
            return self.conv[column](string)
        except ObjectDoesNotExist:
            print >>sys.stderr, column, self.referred[self.column[column]], string
            raise

    def make_model_args(self, row):
        ret = {}
        for i, x in enumerate(row):
            fn = self.get_field_name(i)
            if fn is None: continue
            ret[fn] = self.get_field_value(i, x.decode("UTF-8"))
        return ret

    def import_csv(self, datafile, is_dry=True, is_force=False, **kwargs):
        f = csv.reader(open(datafile), **kwargs)
        header = f.next()
        self.set_header(header)
        for row in f:
            if len(row) == 0 or (len(row[0]) != 0 and row[0][0] == '#'):
                continue
            try:
                make_model_kwargs = self.make_model_args(row)
            except ObjectDoesNotExist:
                print >>sys.stderr, row
                if not is_force: raise
            if self.model.objects.filter(**make_model_kwargs).count() == 0:
                if DEBUG: print "create:", make_model_kwargs
                obj = self.model(**make_model_kwargs)
                if not is_dry:
                    obj.save()
            else:
                if DEBUG: print "ignore:", make_model_kwargs
        return


def csv_into_entry():
        cats = [Category.objects.get(code=i.strip()) for i in row[column["category"]].split(",")]
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
    help = 'Import data from traindb'
    args = "csvfile"
    option_list = BaseCommand.option_list + (
        make_option('--delimiter', action='store', dest='delimiter',
                    default=',', help="CSV delimiter character."),
        make_option('--quotechar', action='store', dest='quotechar',
                    default='"', help="CSV quotation character."),
        make_option('-n', '--dry-run', action='store_true', dest='dry',
                    default=False, help="Only print data without importing."),
        make_option('-f', '--force', action='store_true', dest='force',
                    default=False, help="Force not to stop."),
        make_option('--config', action='store', dest='config',
                    default=None, help="Set config file."),
        make_option('--model', action='store', dest='model',
                    default=None, help="Set target model without config."),
        )

    def handle(self, *csv_labels, **option):
        is_dry = option.get('dry')
        is_force = option.get('force')
        delimiter = option.get('delimiter')
        quotechar = option.get('quotechar')
        config = option.get('config')
        model = option.get('model')
        manager = CSVConfigManager(config, model)
        for i in csv_labels:
            print i
            manager.import_csv(i, is_dry=is_dry, is_force=is_force,
                               delimiter=delimiter, quotechar=quotechar)
