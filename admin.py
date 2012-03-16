from django.contrib import admin
from models import EnglishAndLocalizedNameObject
from models import Country, DomesticRegion, District
from models import CompanyType, Company
from models import Line, Station, AdjacentStation


LIST_OF_DOUBLE_NAME = ('local_name', 'english_name')


class CountryAdmin(admin.ModelAdmin):
    list_display = LIST_OF_DOUBLE_NAME + ('codei', 'code2', 'code3')


class DomesticRegionAdmin(admin.ModelAdmin):
    list_display = LIST_OF_DOUBLE_NAME + ('country',)


class DistrictAdmin(admin.ModelAdmin):
    list_display = LIST_OF_DOUBLE_NAME + ('domesticregion', 'code')


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'companytype')


class LineAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'company', 'line_type',
                    'code', 'sort', 'enabled', 'defunct_date')


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'line', 'district', 'enabled')


admin.site.register(Country, CountryAdmin)
admin.site.register(DomesticRegion, DomesticRegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(CompanyType)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(AdjacentStation)
