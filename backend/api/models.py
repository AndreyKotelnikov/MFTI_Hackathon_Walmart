import json
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField


class PredictionBase(models.Model):

    prediction_date = models.DateField()
    store_code = models.CharField(max_length=255)
    store_item_code = models.CharField(max_length=255)
    month_oct = models.BooleanField()
    days_to_nearest_holiday = models.IntegerField()
    rolling_sales_mean_3d = models.FloatField()
    rolling_sales_mean_7d = models.FloatField()
    tavg = models.FloatField()
    tmax = models.FloatField()
    tmin = models.FloatField()
    depart = models.FloatField()
    RA = models.FloatField()
    SN = models.FloatField()
    preciptotal = models.FloatField()
    item_nbr = models.IntegerField()
    dewpoint = models.FloatField()
    wetbulb = models.FloatField()
    heat = models.FloatField()
    cool = models.FloatField()
    snowfall = models.FloatField()
    sealevel = models.FloatField()
    resultspeed = models.FloatField()
    resultdir = models.FloatField()
    avgspeed = models.FloatField()
    BCFG = models.FloatField()
    BLDU = models.FloatField()
    BLSN = models.FloatField()
    BR = models.FloatField()
    DU = models.FloatField()
    DZ = models.FloatField()
    FG = models.FloatField()
    FG_plus = models.FloatField(db_column='FG+')
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
    SG = models.FloatField()
    SQ = models.FloatField()
    TS = models.FloatField()
    TSRA = models.FloatField()
    TSSN = models.FloatField()
    UP = models.FloatField()
    VCFG = models.FloatField()
    VCTS = models.FloatField()
    filled = models.BooleanField()
    weekend = models.IntegerField()
    _fri = models.BooleanField()
    _mon = models.BooleanField()
    _sat = models.BooleanField()
    _sun = models.BooleanField()
    _thu = models.BooleanField()
    _tue = models.BooleanField()
    _wed = models.BooleanField()
    month_apr = models.BooleanField()
    month_aug = models.BooleanField()
    month_dec = models.BooleanField()
    month_feb = models.BooleanField()
    month_jan = models.BooleanField()
    month_jul = models.BooleanField()
    month_jun = models.BooleanField()
    month_mar = models.BooleanField()
    month_may = models.BooleanField()
    month_nov = models.BooleanField()
    month_sep = models.BooleanField()
    season_autumn = models.BooleanField()
    season_spring = models.BooleanField()
    season_summer = models.BooleanField()
    season_winter = models.BooleanField()
    day_of_year = models.IntegerField()
    temperature_diff = models.FloatField()
    heavy_precip = models.IntegerField()
    max_temp_last_3_days = models.FloatField()
    avg_temp_last_3_days = models.FloatField()
    avg_precip_last_3_days = models.FloatField()
    avg_sealevel_last_3_days = models.FloatField()
    avg_speed_last_3_days = models.FloatField()
    is_holiday = models.IntegerField()
    avg_daily_sales_item = models.FloatField()
    store_sales_rank = models.FloatField()
    item_sales_rank = models.FloatField()
    zero_sales_count_7d = models.FloatField()
    shap = models.CharField(null=True)
    units = models.FloatField(null=True)
    units_pred = models.FloatField(null=True)

    # prediction_date = models.DateField()
    # store_code = models.CharField(max_length=250)
    # store_item_code = models.CharField(max_length=250)
    # units_yesterday = models.FloatField()
    # units_prev_week = models.FloatField()
    # tmax = models.FloatField()
    # tmin = models.FloatField()
    # tavg = models.FloatField()
    # depart = models.FloatField()
    # dewpoint = models.FloatField()
    # wetbulb = models.FloatField()
    # heat = models.FloatField()
    # cool = models.FloatField()
    # sunrise = models.FloatField()
    # sunset = models.FloatField()
    # snowfall = models.FloatField()
    # preciptotal = models.FloatField()
    # stnpressure = models.FloatField()
    # sealevel = models.FloatField()
    # resultspeed = models.FloatField()
    # resultdir = models.FloatField()
    # avgspeed = models.FloatField()
    # year = models.FloatField()
    # week = models.FloatField()
    # BCFG = models.FloatField()
    # BLDU = models.FloatField()
    # BLSN = models.FloatField()
    # BR = models.FloatField()
    # DU = models.FloatField()
    # DZ = models.FloatField()
    # FG = models.FloatField()
    # FU = models.FloatField()
    # FZDZ = models.FloatField()
    # FZFG = models.FloatField()
    # FZRA = models.FloatField()
    # GR = models.FloatField()
    # GS = models.FloatField()
    # HZ = models.FloatField()
    # MIFG = models.FloatField()
    # PL = models.FloatField()
    # PRFG = models.FloatField()
    # RA = models.FloatField()
    # SG = models.FloatField()
    # SN = models.FloatField()
    # SQ = models.FloatField()
    # TS = models.FloatField()
    # TSRA = models.FloatField()
    # TSSN = models.FloatField()
    # UP = models.FloatField()
    # VCFG = models.FloatField()
    # VCTS = models.FloatField()
    # day_of_week = models.FloatField()
    # month = models.FloatField()
    # is_weekend = models.FloatField()
    # is_holiday = models.FloatField()
    # rain_streak = models.FloatField()
    # dry_streak = models.FloatField()
    # avg_temp_next_day = models.FloatField()
    # rain_next_day = models.FloatField()
    # days_to_holiday = models.FloatField()
    # units = models.FloatField(null=True)
    # units_pred = models.FloatField(null=True)
    # shap = models.JSONField(null=True)

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
    units_real = models.FloatField(verbose_name='Реально продано', null=True)
    units_change = models.FloatField(verbose_name='Проданно при иной погоде', null=True)
    units_over = models.FloatField(verbose_name='Превышение спроса', null=True)
    avg_ratio = models.FloatField(verbose_name='Средний коэффициент', null=True)
    items_ratios_json = models.JSONField(verbose_name='Коэффициенты для итемнов', null=True)

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


class PredictionKat(PredictionBase):

    class Meta:
        verbose_name = 'Предсказание по погоде'
        verbose_name_plural = 'Предсказания по погоде'
        db_table = 'kat_table_with_pred'
        managed = False


class PredictionResearch(PredictionBase):

    research = models.ForeignKey(Research, on_delete=models.CASCADE)
    real = models.ForeignKey(PredictionKat, on_delete=models.CASCADE)
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

