import random
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api.models import PredictionWithout
from api.models import PredictionReal
from api.models import MeteoStation
from api.models import Store
from hackathon.sources_db import runQuery


class MeteoStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeteoStation
        fields = (
            'station_nbr',
            'city',
            'state',
            'latitude',
            'longitude',
        )


class StoreSerializer(serializers.ModelSerializer):

    station_detail = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = (
            'store_nbr',
            'name',
            'title',
            'station',
            'station_detail',
        )

    def get_station_detail(self, obj):
        return MeteoStationSerializer(obj.station).data

    def get_title(self, obj):
        return f'Walmart #{obj.store_nbr}'


class PredictionListSerializer(serializers.ModelSerializer):
    
    pred_without = serializers.ReadOnlyField()
    difference = serializers.SerializerMethodField()
    coefficient = serializers.SerializerMethodField()

    class Meta:
        model = PredictionReal
        fields = (
            'id',
            'prediction_date',
            'store_code',
            'store_item_code',
            'tavg',
            'RA',
            'units',
            'units_pred',
            'pred_without',
            'difference',
            'coefficient',
        )

    def get_difference(self, obj):
        return obj.units_pred - obj.pred_without

    def get_coefficient(self, obj):
        return obj.units_pred / obj.pred_without        


class PredictionRealSerializer(PredictionListSerializer):

    class Meta(PredictionListSerializer.Meta):

        model = PredictionReal

        fields = PredictionListSerializer.Meta.fields + (
            'units_yesterday', 'units_prev_week', 
            'tmax', 'tmin', 'depart', 'dewpoint', 'wetbulb', 'heat', 'cool', 'sunrise', 
            'sunset', 'snowfall', 'preciptotal', 'stnpressure', 'sealevel', 'resultspeed', 
            'resultdir', 'avgspeed', 'year', 'week', 'BCFG', 'BLDU', 'BLSN', 'BR', 'DU', 'DZ', 
            'FG', 'FU', 'FZDZ', 'FZFG', 'FZRA', 'GR', 'GS', 'HZ', 'MIFG', 'PL', 'PRFG', 'SG', 
            'SN', 'SQ', 'TS', 'TSRA', 'TSSN', 'UP', 'VCFG', 'VCTS', 'day_of_week', 'month', 
            'is_weekend', 'is_holiday', 'rain_streak', 'dry_streak', 'avg_temp_next_day', 
            'rain_next_day', 'days_to_holiday'
        )

