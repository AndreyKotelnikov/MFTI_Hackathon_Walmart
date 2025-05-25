import json
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api.models import PredictionWithout
from api.models import PredictionReal
from api.models import MeteoStation
from api.models import Store
from hackathon.sources_db import runQuery
from django.forms.models import model_to_dict


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
    
    pred_without = serializers.ReadOnlyField(source='pred_without.units_pred')
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
        units_pred_without = obj.pred_without.units_pred if obj.pred_without else None
        if not units_pred_without:
            return 0
        if obj.units_pred == 0 or units_pred_without == 0:
            return 0
        return obj.units_pred - units_pred_without

    def get_coefficient(self, obj):
        units_pred_without = obj.pred_without.units_pred if obj.pred_without else None
        if not units_pred_without:
            return 0
        if obj.units_pred == 0 or units_pred_without == 0:
            return 0
        return obj.units_pred / units_pred_without


class PredictionDetailSerializer(serializers.ModelSerializer):

    shap = serializers.SerializerMethodField()

    class Meta:
        model = PredictionReal
        fields = (
            'tavg', 'RA', 'units_pred', 'store_code', 'store_item_code',
            'units_yesterday', 'units_prev_week', 
            'tmax', 'tmin', 'depart', 'dewpoint', 'wetbulb', 'heat', 'cool', 'sunrise', 
            'sunset', 'snowfall', 'preciptotal', 'stnpressure', 'sealevel', 'resultspeed', 
            'resultdir', 'avgspeed', 'year', 'week', 'BCFG', 'BLDU', 'BLSN', 'BR', 'DU', 'DZ', 
            'FG', 'FU', 'FZDZ', 'FZFG', 'FZRA', 'GR', 'GS', 'HZ', 'MIFG', 'PL', 'PRFG', 'SG', 
            'SN', 'SQ', 'TS', 'TSRA', 'TSSN', 'UP', 'VCFG', 'VCTS', 'day_of_week', 'month', 
            'is_weekend', 'is_holiday', 'rain_streak', 'dry_streak', 'avg_temp_next_day', 
            'rain_next_day', 'days_to_holiday', 'shap',
        )
        
    def get_shap(self, obj):
        return json.loads(obj.shap.replace("'", '"'))

class PredictionRealSerializer(PredictionListSerializer):

    real_detail = serializers.SerializerMethodField()
    without_detail = serializers.SerializerMethodField()

    class Meta(PredictionListSerializer.Meta):

        model = PredictionReal

        fields = PredictionListSerializer.Meta.fields + (
            'real_detail', 'without_detail',
        )

    def get_real_detail(self, obj):
        return PredictionDetailSerializer(obj, many=False).data

    def get_without_detail(self, obj):
        return PredictionDetailSerializer(obj.pred_without, many=False).data
