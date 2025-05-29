import json
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api.models import PredictionResearch
from api.models import PredictionKat
from api.models import MeteoStation
from api.models import Store
from api.models import Research
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
        return f'Магазин #{obj.store_nbr}'


class PredictionListSerializer(serializers.ModelSerializer):
    
    real_pred = serializers.ReadOnlyField(source='real.units_pred')

    class Meta:
        model = PredictionResearch
        fields = (
            'id',
            'prediction_date',
            'store_code',
            'store_item_code',
            'tavg',
            'RA',
            'units',
            'units_pred',
            'real_pred',
            'difference',
            'coefficient',
        )


class PredictionDetailSerializer(serializers.ModelSerializer):

    shap = serializers.SerializerMethodField()

    class Meta:
        model = PredictionKat
        fields = (
            'prediction_date', 'store_code', 'store_item_code', 'month_oct', 'days_to_nearest_holiday', 'rolling_sales_mean_3d', 'rolling_sales_mean_7d', 'units_pred', 
            'tavg', 'tmax', 'tmin', 'depart', 'RA', 'SN', 'preciptotal', 'item_nbr', 'dewpoint', 'wetbulb', 'heat', 'cool', 'snowfall', 'sealevel', 'resultspeed', 'resultdir', 
            'avgspeed', 'BCFG', 'BLDU', 'BLSN', 'BR', 'DU', 'DZ', 'FG', 'FG_plus', 'FU', 'FZDZ', 'FZFG', 'FZRA', 'GR', 'GS', 'HZ', 'MIFG', 'PL', 'PRFG', 'SG', 'SQ', 'TS', 'TSRA', 
            'TSSN', 'UP', 'VCFG', 'VCTS', 'filled', 'weekend', '_fri', '_mon', '_sat', '_sun', '_thu', '_tue', '_wed', 'month_apr', 'month_aug', 'month_dec', 'month_feb', 'month_jan', 
            'month_jul', 'month_jun', 'month_mar', 'month_may', 'month_nov', 'month_sep', 'season_autumn', 'season_spring', 'season_summer', 'season_winter', 'day_of_year', 
            'temperature_diff', 'heavy_precip', 'max_temp_last_3_days', 'avg_temp_last_3_days', 'avg_precip_last_3_days', 'avg_sealevel_last_3_days', 'avg_speed_last_3_days', 
            'is_holiday', 'avg_daily_sales_item', 'store_sales_rank', 'item_sales_rank', 'zero_sales_count_7d', 'shap'
        )
        
    def get_shap(self, obj):
        if type(obj.shap) == dict:
            return obj.shap
        if not obj.shap:
            return {}
        return json.loads(obj.shap.replace("'", '"'))


class PredictionResearchSerializer(PredictionListSerializer):

    real_detail = serializers.SerializerMethodField()
    research_detail = serializers.SerializerMethodField()

    class Meta(PredictionListSerializer.Meta):

        model = PredictionResearch

        fields = PredictionListSerializer.Meta.fields + (
            'real_detail', 'research_detail',
        )

    def get_real_detail(self, obj):
        return PredictionDetailSerializer(obj.real, many=False).data

    def get_research_detail(self, obj):
        return PredictionDetailSerializer(obj, many=False).data


class ResearchSerializer(serializers.ModelSerializer):

    mode = serializers.CharField(required=True)
    period_start = serializers.DateField(required=True)
    period_end = serializers.DateField(required=True)
    avg_temp = serializers.IntegerField(required=True)
    precip_amount = serializers.IntegerField(required=True)

    class Meta:
        model = Research
        fields = '__all__'
        read_only_fields = ('created_at',)
