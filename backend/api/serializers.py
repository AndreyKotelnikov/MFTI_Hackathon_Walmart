import json
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api.models import PredictionResearch
from api.models import PredictionReal
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
        return f'Walmart #{obj.store_nbr}'


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
