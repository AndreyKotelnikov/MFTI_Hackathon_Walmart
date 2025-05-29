from django.contrib import admin

from api.models import PredictionResearch
from api.models import PredictionKat
from api.models import MeteoStation
from api.models import Store
from api.models import Research


@admin.register(PredictionResearch)
class PredictionResearchAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'prediction_date',
        'store_item_code',
        'units_pred'
    ]
    list_select_related = ('research', 'real')  # Оптимизация запросов
    raw_id_fields = ('real', 'research')  # Замена выпадающего списка на поиск по ID
    
    def real_id(self, obj):
        return obj.real.id if obj.real else None
    real_id.short_description = 'Real ID'

@admin.register(PredictionKat)
class PredictionKatAdmin(admin.ModelAdmin):
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


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = [
        'created_at',
        'mode',
        'period_start',
        'period_end',
        'avg_temp',
        'precip_amount',
    ]


