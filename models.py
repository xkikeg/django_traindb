from django.db import models
from django.utils.translation import ugettext as _


class Country(models.Model):

    """Country"""

    codei = models.PositiveSmallIntegerField(_("ISO 3166-1 numeric"),
                                             primary_key=True)
    code2 = models.SlugField(_("ISO 3166-1 alpha-2"),
                             max_length=2,
                             unique=True)
    code3 = models.SlugField(_("ISO 3166-1 alpha-3"),
                             max_length=3,
                             unique=True)
    englishName = models.CharField(_("Country name in English"),
                                   max_length=128)
    localName = models.CharField(_("Country name in local language"),
                                 max_length=256)


class Area(models.Model):

    """Wide area in the country"""

    country = models.ForeignKey(Country)
    englishName = models.CharField(_("name of the area in English"),
                                   max_length=128)
    localName = models.CharField(_("name of the area in local language"),
                                 max_length=128)


class District(models.Model):

    """Smaller area in the country"""

    area = models.ForeignKey(Area)
    code = models.SlugField(_("ISO 3166-2"),
                            max_length=6)
    englishName = models.CharField(_("name of the district in English"),
                                   max_length=128)
    localName = models.CharField(_("name of the district in local language"),
                                 max_length=128)


class CompanyType(models.Model):

    """The type of the railway company"""

    description = models.CharField(_("type of the railway"),
                                   max_length=64)


class Company(models.Model):

    """Railway company"""

    companyType = models.ForeignKey(CompanyType)
    name = models.CharField(_("name of the company"),
                            max_length=256)


class Line(models.Model):

    """Railway line"""

    company = models.ForeignKey(Company)
    code = models.IntegerField(_("the line code in ekidata"),
                               blank=True,
                               null=True,
                               unique=True)
    sort = models.IntegerField(_("sort key with line in ekidata"),
                               blank=True,
                               null=True)
    name = models.CharField(_("name of the line"),
                            max_length=256)
    enabled = models.BooleanField(_("Enabled"))


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
    district = models.ForeignKey(District)
    isUnderground = models.BooleanField(_("Subway station"))
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
