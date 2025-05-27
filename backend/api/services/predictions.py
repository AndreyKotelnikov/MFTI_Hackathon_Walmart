import pandas as pd
from api.models import PredictionReal
from django.db import transaction
from api.models import PredictionReal, PredictionResearch, Research

def get_research_predictions(research):
    queryset = PredictionReal.objects.filter(
        prediction_date__gte=research.period_start,
        prediction_date__lte=research.period_end,
    )
    if research.store_code:
        queryset = queryset.filter(store_code=research.store_code)
        if research.store_item_code:
            queryset = queryset.filter(store_item_code=research.store_item_code)
    
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
    :param real_prediction: объект PredictionReal
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
    tmin_f = (2 * avg_temp_f) / (original_ratio + 1)
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
    :param real_predictions: QuerySet или список PredictionReal объектов
    :return: Список созданных PredictionResearch объектов
    """
    # Создаем PredictionResearch для каждого PredictionReal
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
                units_yesterday=real.units_yesterday,
                units_prev_week=real.units_prev_week,
                dewpoint=real.dewpoint,
                wetbulb=real.wetbulb,
                heat=real.heat,
                cool=real.cool,
                sunrise=real.sunrise,
                sunset=real.sunset,
                snowfall=real.snowfall,
                stnpressure=real.stnpressure,
                sealevel=real.sealevel,
                resultspeed=real.resultspeed,
                resultdir=real.resultdir,
                avgspeed=real.avgspeed,
                year=real.year,
                week=real.week,
                BCFG=real.BCFG,
                BLDU=real.BLDU,
                BLSN=real.BLSN,
                BR=real.BR,
                DU=real.DU,
                DZ=real.DZ,
                FG=real.FG,
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
                day_of_week=real.day_of_week,
                month=real.month,
                is_weekend=real.is_weekend,
                is_holiday=real.is_holiday,
                rain_streak=real.rain_streak,
                dry_streak=real.dry_streak,
                avg_temp_next_day=real.avg_temp_next_day,
                rain_next_day=real.rain_next_day,
                days_to_holiday=real.days_to_holiday,
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
