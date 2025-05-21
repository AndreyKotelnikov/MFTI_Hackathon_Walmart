import json
from django.db import models
from django.contrib.postgres.fields import ArrayField


class PredictionBase(models.Model):

    prediction_date = models.DateField()
    store_code = models.CharField(max_length=250)
    store_item_code = models.CharField(max_length=250)
    units_yesterday = models.FloatField()
    units_prev_week = models.FloatField()
    tmax = models.FloatField()
    tmin = models.FloatField()
    tavg = models.FloatField()
    depart = models.FloatField()
    dewpoint = models.FloatField()
    wetbulb = models.FloatField()
    heat = models.FloatField()
    cool = models.FloatField()
    sunrise = models.FloatField()
    sunset = models.FloatField()
    snowfall = models.FloatField()
    preciptotal = models.FloatField()
    stnpressure = models.FloatField()
    sealevel = models.FloatField()
    resultspeed = models.FloatField()
    resultdir = models.FloatField()
    avgspeed = models.FloatField()
    year = models.FloatField()
    week = models.FloatField()
    BCFG = models.FloatField()
    BLDU = models.FloatField()
    BLSN = models.FloatField()
    BR = models.FloatField()
    DU = models.FloatField()
    DZ = models.FloatField()
    FG = models.FloatField()
    FU = models.FloatField()
    FZDZ = models.FloatField()
    FZFG = models.FloatField()
    FZRA = models.FloatField()
    GR = models.FloatField()
    GS = models.FloatField()
    HZ = models.FloatField()
    MIFG = models.FloatField()
    PL = models.FloatField()
    PRFG = models.FloatField()
    RA = models.FloatField()
    SG = models.FloatField()
    SN = models.FloatField()
    SQ = models.FloatField()
    TS = models.FloatField()
    TSRA = models.FloatField()
    TSSN = models.FloatField()
    UP = models.FloatField()
    VCFG = models.FloatField()
    VCTS = models.FloatField()
    day_of_week = models.FloatField()
    month = models.FloatField()
    is_weekend = models.FloatField()
    is_holiday = models.FloatField()
    rain_streak = models.FloatField()
    dry_streak = models.FloatField()
    avg_temp_next_day = models.FloatField()
    rain_next_day = models.FloatField()
    days_to_holiday = models.FloatField()
    units = models.FloatField()
    units_pred = models.FloatField()

    class Meta:
        abstract = True


class PredictionWithout(PredictionBase):

    class Meta:
        verbose_name = 'Беспогодное предсказание'
        verbose_name_plural = 'Беспогодные предсказания'
        db_table = 'prediction_base_weather'
        managed = False


class PredictionReal(PredictionBase):

    class Meta:
        verbose_name = 'Предсказание по погоде'
        verbose_name_plural = 'Предсказания по погоде'
        db_table = 'prediction_real_weather'
        managed = False

    @property
    def pred_without(self):
        p = PredictionWithout.objects.filter(
            prediction_date = self.prediction_date,
            store_item_code = self.store_item_code
        ).first()
        return p.units_pred if p else None


class MeteoStation(models.Model):

    station_nbr = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        verbose_name = 'Метеостанция'
        verbose_name_plural = 'Метеостанции'
        db_table = 'stations'
        managed = False

    def __str__(self):
        return self.city


class Store(models.Model):

    store_nbr = models.IntegerField(primary_key=True)
    station = models.ForeignKey(MeteoStation, on_delete=models.PROTECT, db_column='station_nbr')
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        db_table = 'stores'
        managed = False

