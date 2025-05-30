import pandas as pd
from api.models import PredictionKat
from api.models import PredictionKat, PredictionResearch, Research
from collections import defaultdict
from django.db import transaction

def get_research_predictions(research):
    queryset = PredictionKat.objects.filter(
        prediction_date__gte=research.period_start,
        prediction_date__lte=research.period_end,
    )
    if research.store_code:
        queryset = queryset.filter(store_code=research.store_code.replace('s', ''))
        if research.store_item_code:
            queryset = queryset.filter(store_item_code=research.store_item_code.replace('-', '_'))
    
    return queryset.all()


def celsius_to_fahrenheit(c):
    """Конвертация °C в °F"""
    return (c * 9/5) + 32

def mm_to_inches(mm):
    """Конвертация мм в дюймы"""
    return mm / 25.4

def calculate_weather_override(real_prediction, research):
    """
    Генерирует параметры погоды на основе research
    :param real_prediction: объект PredictionKat
    :param research: объект Research
    :return: dict с обновлёнными параметрами
    """
    # Конвертация единиц измерения
    avg_temp_f = celsius_to_fahrenheit(research.avg_temp)
    precip_in = mm_to_inches(research.precip_amount)
    
    # Сохраняем оригинальное соотношение tmax/tmin
    if real_prediction.tmax and real_prediction.tmin:
        original_ratio = real_prediction.tmax / real_prediction.tmin if real_prediction.tmin != 0 else 1
    else:
        original_ratio = 1.2  # Дефолтное соотношение, если нет данных
    
    # Вычисляем новые tmax и tmin (в °F)
    # (tmax + tmin)/2 = avg_temp => tmax = 2*avg_temp - tmin
    # И сохраняем соотношение tmax/tmin = original_ratio
    tmin_f = (2 * avg_temp_f) / (original_ratio + 1) if (original_ratio + 1) != 0 else (2 * avg_temp_f) / 2.2
    tmax_f = 2 * avg_temp_f - tmin_f
    
    # Вычисляем новый depart (отклонение от нормы)
    # Предполагаем, что original_depart = real_prediction.tavg - климатическая норма
    # Новый depart = новый tavg - (оригинальный tavg - оригинальный depart)
    new_depart = avg_temp_f - (real_prediction.tavg - real_prediction.depart) if hasattr(real_prediction, 'tavg') else 0
    
    return {
        'tavg': avg_temp_f,
        'tmax': tmax_f,
        'tmin': tmin_f,
        'depart': new_depart,
        'RA': 1 if research.is_rain else 0,
        'SN': 1 if research.is_snow else 0,
        'preciptotal': precip_in,
    }


def create_research_predictions(research, real_predictions):
    """
    Создает PredictionResearch объекты для указанного исследования
    
    :param research: исследование (Research)
    :param real_predictions: QuerySet или список PredictionKat объектов
    :return: Список созданных PredictionResearch объектов
    """
    # Создаем PredictionResearch для каждого PredictionKat
    research_predictions = []
    for real in real_predictions:
        
        weather_override = calculate_weather_override(real, research)

        research_predictions.append(
            PredictionResearch(
                research=research,
                real=real,

                prediction_date=real.prediction_date,
                store_code=real.store_code,
                store_item_code=real.store_item_code,
                month_oct=real.month_oct,
                days_to_nearest_holiday=real.days_to_nearest_holiday,
                rolling_sales_mean_3d=real.rolling_sales_mean_3d,
                rolling_sales_mean_7d=real.rolling_sales_mean_7d,
                item_nbr=real.item_nbr,
                dewpoint=real.dewpoint,
                wetbulb=real.wetbulb,
                heat=real.heat,
                cool=real.cool,
                snowfall=real.snowfall,
                sealevel=real.sealevel,
                resultspeed=real.resultspeed,
                resultdir=real.resultdir,
                avgspeed=real.avgspeed,
                BCFG=real.BCFG,
                BLDU=real.BLDU,
                BLSN=real.BLSN,
                BR=real.BR,
                DU=real.DU,
                DZ=real.DZ,
                FG=real.FG,
                FG_plus=real.FG_plus,
                FU=real.FU,
                FZDZ=real.FZDZ,
                FZFG=real.FZFG,
                FZRA=real.FZRA,
                GR=real.GR,
                GS=real.GS,
                HZ=real.HZ,
                MIFG=real.MIFG,
                PL=real.PL,
                PRFG=real.PRFG,
                SG=real.SG,
                SQ=real.SQ,
                TS=real.TS,
                TSRA=real.TSRA,
                TSSN=real.TSSN,
                UP=real.UP,
                VCFG=real.VCFG,
                VCTS=real.VCTS,
                filled=real.filled,
                weekend=real.weekend,
                _fri=real._fri,
                _mon=real._mon,
                _sat=real._sat,
                _sun=real._sun,
                _thu=real._thu,
                _tue=real._tue,
                _wed=real._wed,
                month_apr=real.month_apr,
                month_aug=real.month_aug,
                month_dec=real.month_dec,
                month_feb=real.month_feb,
                month_jan=real.month_jan,
                month_jul=real.month_jul,
                month_jun=real.month_jun,
                month_mar=real.month_mar,
                month_may=real.month_may,
                month_nov=real.month_nov,
                month_sep=real.month_sep,
                season_autumn=real.season_autumn,
                season_spring=real.season_spring,
                season_summer=real.season_summer,
                season_winter=real.season_winter,
                day_of_year=real.day_of_year,
                temperature_diff=real.temperature_diff,
                heavy_precip=real.heavy_precip,
                max_temp_last_3_days=real.max_temp_last_3_days,
                avg_temp_last_3_days=real.avg_temp_last_3_days,
                avg_precip_last_3_days=real.avg_precip_last_3_days,
                avg_sealevel_last_3_days=real.avg_sealevel_last_3_days,
                avg_speed_last_3_days=real.avg_speed_last_3_days,
                is_holiday=real.is_holiday,
                avg_daily_sales_item=real.avg_daily_sales_item,
                store_sales_rank=real.store_sales_rank,
                item_sales_rank=real.item_sales_rank,
                zero_sales_count_7d=real.zero_sales_count_7d,
                units=real.units,

                # tmax=real.tmax,
                # tmin=real.tmin,
                # tavg=real.tavg,
                # depart=real.depart,
                # RA=real.RA,
                # SN=real.SN,
                # preciptotal=real.preciptotal,
                # Копируем оригинальные значения
                # **{k: getattr(real, k) for k in [
                #     'tavg', 'tmax', 'tmin', 'depart',
                #     'RA', 'SN', 'preciptotal'
                # ] if hasattr(real, k)},
                # Перезаписываем модифицированными значениями
                **weather_override
            )
        )
    
    # Массовое создание объектов
    created_predictions = PredictionResearch.objects.bulk_create(research_predictions)
    
    return created_predictions


def group_by_store(data):
    """
    Группирует записи по идентификатору магазина (первая цифра в store_item_code)
    
    :param data: Список словарей формата [{'store_item_code': 'X-XXX', 'ratio': float}, ...]
    :return: Словарь {store_id: [записи_магазина], ...}
    """
    grouped = defaultdict(list)
    
    for item in data:
        # Извлекаем первую цифру до дефиса как идентификатор магазина
        store_id = 's' + item['store_item_code'].split('_')[0]
        grouped[store_id].append(item)
    
    return dict(grouped)