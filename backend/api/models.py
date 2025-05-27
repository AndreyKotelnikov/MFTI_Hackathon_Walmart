import json
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    units = models.FloatField(null=True)
    units_pred = models.FloatField(null=True)
    shap = models.JSONField(null=True)

    class Meta:
        abstract = True


class Research(models.Model):
    MODE_CHOICES = [
        ('week', 'Неделя'),
        ('month', 'Месяц'),
        ('season', 'Сезон'),
        ('period', 'Период'),
    ]
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, verbose_name='Период')
    period_start = models.DateField(verbose_name='Начало периода')
    period_end = models.DateField(verbose_name='Конец периода')
    store_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='Код магазина')
    store_item_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='Код товара')
    is_rain = models.BooleanField(default=False, verbose_name='Дождь')
    is_snow = models.BooleanField(default=False, verbose_name='Снег')
    avg_temp = models.IntegerField(
        validators=[MinValueValidator(-50), MaxValueValidator(50)],
        verbose_name='Средняя температура'
    )
    precip_amount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        verbose_name='Количество осадков (мм)'
    )

    class Meta:
        verbose_name = 'Исследование'
        verbose_name_plural = 'Исследования'
        ordering = ['-created_at']

    def __str__(self):
        return f"Исследование от {self.created_at.strftime('%Y-%m-%d')}"


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


class PredictionResearch(PredictionBase):

    research = models.ForeignKey(Research, on_delete=models.CASCADE)
    real = models.ForeignKey(PredictionReal, on_delete=models.CASCADE)
    difference = models.FloatField(verbose_name='Разница с реальным предсказанием', default=0)
    coefficient = models.FloatField(verbose_name='Отношение к реальному предсказанию', default=1)

    class Meta:
        verbose_name = 'Предсказание для исследования'
        verbose_name_plural = 'Предсказания для исследований'


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

