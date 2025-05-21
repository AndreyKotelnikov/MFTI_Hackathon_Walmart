from django.contrib import admin

from api.models import PredictionWithout
from api.models import PredictionReal
from api.models import MeteoStation
from api.models import Store


@admin.register(PredictionWithout)
class PredictionWithoutAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'prediction_date',
        'store_item_code',
        'units_pred'
    ]


@admin.register(PredictionReal)
class PredictionRealAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'prediction_date',
        'store_item_code',
        'units_pred'
    ]


@admin.register(MeteoStation)
class MeteoStationAdmin(admin.ModelAdmin):
    list_display = [
        'station_nbr',
        'state',
        'city',
    ]


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = [
        'station',
        'store_nbr',
    ]


