from django.db import models
from django.utils.translation import ugettext_lazy as _

MAX_KILO_DIGITS = 6
MAX_ENGLISH_NAME = 128
MAX_LOCALIZED_NAME = 256
MAX_LINE_NAME_LENGTH = 128
MAX_LINE_NICKNAME_LENGTH = 128


class EnglishAndLocalizedNameObject(models.Model):

    """Abstract class for object with English and localized name."""

    english_name = models.CharField(_("English name"),
                                    max_length=MAX_ENGLISH_NAME)
    local_name = models.CharField(_("localized name"),
                                  max_length=MAX_LOCALIZED_NAME)

    class Meta:
        abstract = True
        ordering = ('local_name', 'english_name')

    def __unicode__(self):
        return self.local_name


class Country(EnglishAndLocalizedNameObject):

    """Country"""

    codei = models.PositiveSmallIntegerField(_("ISO 3166-1 numeric"),
                                             primary_key=True)
    code2 = models.SlugField(_("ISO 3166-1 alpha-2"),
                             max_length=2,
                             unique=True)
    code3 = models.SlugField(_("ISO 3166-1 alpha-3"),
                             max_length=3,
                             unique=True)

    class Meta:
        ordering = (('code2', 'code3')
                    + EnglishAndLocalizedNameObject.Meta.ordering)


class DomesticRegion(EnglishAndLocalizedNameObject):

    """wider area in the country"""

    country = models.ForeignKey(Country)

    class Meta:
        ordering = (('country',)
                    + EnglishAndLocalizedNameObject.Meta.ordering)


class District(EnglishAndLocalizedNameObject):

    """Smaller area in the country"""

    domesticregion = models.ForeignKey(DomesticRegion)
    code = models.SlugField(_("ISO 3166-2"),
                            max_length=6)

    class Meta:
        ordering = (('code',)
                    + EnglishAndLocalizedNameObject.Meta.ordering)


class CompanyType(models.Model):

    """The type of the railway company"""

    description = models.CharField(_("type of the railway"),
                                   max_length=64,
                                   unique=True)

    def __unicode__(self):
        return self.description


class Company(models.Model):

    """Railway company"""

    companytype = models.ForeignKey(CompanyType)
    name = models.CharField(_("name of the company"),
                            max_length=256)

    class Meta:
        ordering = ('companytype', 'id')

    def __unicode__(self):
        return self.name


LINE_TYPE_CHOICES = (
    (1, _("high speed train")),
    (2, _("normal train")),
    (3, _("tram train")),
    (4, _("suspended monorail")),
    (5, _("straddle monorail")),
    (6, _("guideway transit")),
    (7, _("funicular")),
    (8, _("trolleybus")),
    (9, _("Maglev train")),
    )


class Line(models.Model):

    """Railway line"""

    company = models.ForeignKey(Company)
    code = models.IntegerField(_("the line code in ekidata"),
                               blank=True,
                               null=True,
                               unique=True)
    sort = models.IntegerField(_("sort key of line in ekidata"),
                               blank=True,
                               null=True)
    line_type = models.SmallIntegerField(_("technical line type"),
                                         choices=LINE_TYPE_CHOICES)
    name = models.CharField(_("name of the line"),
                            max_length=MAX_LINE_NAME_LENGTH)
    nickname = models.CharField(_("nickname of the line"),
                                max_length=MAX_LINE_NICKNAME_LENGTH,
                                blank=True)
    enabled = models.BooleanField(_("enabled flag"))
    defunct_date = models.DateField(_("date when get defunct if disabled"),
                                    blank=True,
                                    null=True)

    class Meta:
        ordering = ('sort', 'code', 'company', 'name')

    def __unicode__(self):
        return unicode(self.company) + u',' + unicode(self.name)


class Station(models.Model):

    """Railway station"""

    line = models.ForeignKey(Line)
    code = models.IntegerField(_("station code in ekidata"),
                               blank=True,
                               null=True,
                               unique=True)
    sort = models.IntegerField(_("sort key of station in ekidata"),
                               blank=True,
                               null=True)
    group_code = models.IntegerField(_("group code of the station in ekidata"),
                                     blank=True,
                                     null=True)
    name = models.CharField(_("name of the station"),
                            max_length=256)
    kilo = models.DecimalField(_("kilo from the origination"),
                               max_digits=MAX_KILO_DIGITS,
                               decimal_places=1,
                               blank=True,
                               null=True)
    district = models.ForeignKey(District)
    is_underground = models.BooleanField(_("subway station flag"))
    longitude = models.DecimalField(_("longitude of the station"),
                                    max_digits=9,
                                    decimal_places=6)
    latitude = models.DecimalField(_("latitude of the station"),
                                   max_digits=9,
                                   decimal_places=6)
    enabled = models.BooleanField(_("enabled flag"))

    class Meta:
        ordering = ('sort', 'code', 'name')

    def __unicode__(self):
        return unicode(self.line) + u',' + unicode(self.name)


class AdjacentStation(models.Model):

    """Adjacence of the station"""

    line = models.ForeignKey(Line)
    station1 = models.ForeignKey(Station, related_name="adjacent_station1")
    station2 = models.ForeignKey(Station, related_name="adjacent_station2")
    kilo = models.DecimalField(_("kilo between the stations"),
                               max_digits=MAX_KILO_DIGITS,
                               decimal_places=1,
                               blank=True,
                               null=True)
    inter_points = models.CharField(_("intermediate points of the adjacence"),
                                    max_length=2048,
                                    blank=True)

    def __unicode__(self):
        text = (self.line, self.station1.name, self.station2.name)
        return u','.join(unicode(i) for i in text)
