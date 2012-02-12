from django.db import models
from django.utils.translation import ugettext as _


class Country(models.Model):

    """Country"""

    code2 = models.CharField(_("two letter country code"),
                             max_length=2,
                             primary_key=True)
    code3 = models.CharField(_("three letter country code"),
                             max_length=3,
                             unique=True)
    englishName = models.CharField(_("Country name in English"),
                                   max_length=128)
    localName = models.CharField(_("Country name in the local language"),
                                 max_length=256)


class Area(models.Model):

    """Wide area in the country."""

    name = models.CharField(_("name of the area"),
                            max_length=128)
    country = models.ForeignKey(Country)


class Prefecture(models.Model):

    """Prefecture, smaller area in the country"""

    name = models.CharField(_("name of the prefecture"),
                            max_length=128)
    area = models.ForeignKey(Area)


class CompanyType(models.Model):

    """The type of the railway company"""

    name = models.CharField(_("type of the railway"),
                            max_length=64)


class Company(models.Model):

    """Railway company"""

    name = models.CharField(_("name of the company"),
                            max_length=256)
    companyType = models.ForeignKey(CompanyType)


class Line(models.Model):

    """Railway line"""

    code = models.IntegerField(_("the line code in ekidata"),
                               blank=True,
                               null=True,
                               unique=True)
    sort = models.IntegerField(_("sort key with line in ekidata"),
                               blank=True,
                               null=True)
    name = models.CharField(_("name of the line"),
                            max_length=256)
    company = models.ForeignKey(Company)
    enabled = models.BooleanField(_("Enabled"))


class StationType(models.Model):

    """Type of the station"""

    isUnderground = models.BooleanField(_("Underground station"))


class Station(models.Model):

    """Railway station"""

    line = models.ForeignKey(Line)
    code = models.IntegerField(_("station code in ekidata"),
                               blank=True,
                               null=True,
                               unique=True)
    sort = models.IntegerField(_("sort key in ekidata"),
                               blank=True,
                               null=True)
    groupCode = models.IntegerField(_("group code of the station"),
                                    blank=True,
                                    null=True)
    name = models.CharField(_("name of the station"),
                            max_length=256)
    kilo = models.DecimalField(_("kilo from the origination"),
                               max_digits=6,
                               decimal_places=1,
                               blank=True,
                               null=True)
    prefecture = models.ForeignKey(Prefecture)
    stType = models.ForeignKey(StationType)
    longitude = models.DecimalField(_("longitude of the station"),
                                    max_digits=9,
                                    decimal_places=6)
    latitude = models.DecimalField(_("latitude of the station"),
                                   max_digits=9,
                                   decimal_places=6)
    enabled = models.BooleanField(_("Enabled"))


class AdjacentStation(models.Model):

    """Adjacence of the station"""

    station1 = models.ForeignKey(Station)
    station2 = models.ForeignKey(Station)
    kilo = models.DecimalField(_("kilo between the stations"),
                               max_digits=6,
                               decimal_places=1)
    interPoints = models.CharField(_("intermediate points of the adjacence"),
                                   max_length=2048)
