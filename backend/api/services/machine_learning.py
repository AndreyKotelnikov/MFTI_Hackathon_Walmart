import os
import json
from decimal import Decimal
from catboost import Pool
import pandas as pd
from hackathon.sources_db import runQuery
# from catboost import CatBoostClassifier
from django.conf import settings
from django.db import transaction
from api.models import PredictionKat, PredictionResearch, Research
from catboost import CatBoostRegressor, Pool


def load_ml_model(filename):
    model = CatBoostRegressor()
    fullpath = os.path.join(settings.MEDIA_ROOT, 'ml-models', filename)
    model.load_model(fullpath)
    return model


def get_shap_top_features(model, X: pd.DataFrame):
    # Получаем информацию о категориальных фичах из модели
    cat_features_indices = model.get_cat_feature_indices()
    cat_features = []
    
    if cat_features_indices:
        # Получаем имена категориальных фичей по их индексам
        feature_names = model.feature_names_
        cat_features = [feature_names[i] for i in cat_features_indices]
    
    # Проверяем, что все категориальные фичи есть в данных
    cat_features = [col for col in cat_features if col in X.columns]
    
    # Создаем Pool с правильным указанием категориальных фичей
    sample_pool = Pool(
        data=X,
        cat_features=cat_features,
        feature_names=list(X.columns)
    )
    
    try:
        # Получаем SHAP-значения
        shap_values = model.get_feature_importance(type='ShapValues', data=sample_pool)
        
        result = []
        for shap_row in shap_values:
            # Убираем последний элемент (base value) и берём абсолютные значения
            shap_importances = pd.Series(shap_row[:-1], index=X.columns).abs()
            # Сортируем
            top_features = shap_importances.sort_values(ascending=False).to_dict()
            result.append(top_features)
        
        return result
    except Exception as e:
        print(f"Error calculating SHAP values: {str(e)}")
        # Возвращаем пустой словарь или None в случае ошибки
        return [{} for _ in range(len(X))]


def process_predictions_with_ml(research):
    """
    Обрабатывает предсказания через ML модель и обновляет данные
    :param research_id: ID исследования
    """
    # Получаем все PredictionResearch для этого исследования
    research_predictions = PredictionResearch.objects.filter(research_id=research.id).select_related('real')
    
    # Конвертируем в DataFrame для ML обработки
    df = pd.DataFrame.from_records(
        research_predictions.values()
    )
    
    # ML логика:
    model = load_ml_model('catboost_best_model_2.cbm')
    df['store_nbr'] = df['store_code']
    df['FG+'] = df['FG_plus']
    df['units_pred'] = model.predict(df[model.feature_names_])
    items_real_total = {}
    items_research_total = {}
    
    # Обновляем объекты PredictionResearch
    with transaction.atomic():
        for _, row in df.iterrows():
            prediction = research_predictions.get(id=row['id'])
            real_units_pred = prediction.real.units_pred if hasattr(prediction.real, 'units_pred') else 0
            
            prediction.units_pred = row['units_pred'] if row['units_pred'] >= 0 else 0
            
            # Вычисляем разницу и коэффициент
            prediction.difference = row['units_pred'] - real_units_pred
            prediction.coefficient = row['units_pred'] / real_units_pred if real_units_pred != 0 else 0

            store_item_code = row['store_item_code']

            if real_units_pred > 2.6 and prediction.units_pred > 2.6:
                # Итоги по реальным продажам товара
                if store_item_code in items_real_total:
                    items_real_total[store_item_code] += real_units_pred
                else:
                    items_real_total[store_item_code] = real_units_pred

                # Итоги по гипотетическим продажам товара
                if store_item_code in items_research_total:
                    items_research_total[store_item_code] += prediction.units_pred
                else:
                    items_research_total[store_item_code] = prediction.units_pred

            prediction.save()

    # 1. Сумма всех продаж из items_real_total
    sum_real = sum(items_real_total.values())

    # 2. Сумма всех продаж из items_research_total
    sum_research = sum(items_research_total.values())

    # 3. Сумма всех положительных разниц (research - real)
    positive_diffs_sum = sum(
        research_val - real_val 
        for real_val, research_val in zip(items_real_total.values(), items_research_total.values()) 
        if research_val > real_val
    )

    # 4. Массив словарей {store_item_code, ratio}
    ratio_dicts = [
        {'store_item_code': code, 'ratio': items_research_total[code] / items_real_total[code]}
        for code in items_real_total.keys()
        if items_research_total[code] > 3
    ]

    # 5. Среднее всех ratio
    average_ratio = sum(item['ratio'] for item in ratio_dicts) / len(ratio_dicts) if len(ratio_dicts) else 1

    # Вывод результатов
    # print(f"1. Сумма реальных продаж: {sum_real}")
    # print(f"2. Сумма исследовательских продаж: {sum_research}")
    # print(f"3. Сумма положительных разниц: {positive_diffs_sum}")
    # print("4. Массив отношений:")
    # for item in ratio_dicts:
    #     print(f"   {item['store_item_code']}: {item['ratio']:.4f}")
    # print(f"5. Среднее отношение: {average_ratio:.4f}")

    research.units_real = sum_real
    research.units_change = sum_research
    research.units_over = positive_diffs_sum
    research.avg_ratio = average_ratio
    research.items_ratios_json = json.dumps(ratio_dicts)

    research.save()
    
    return research_predictions


def get_prediction_shap(prediction_id):
    research_predictions = PredictionResearch.objects.filter(id=prediction_id).select_related('real')
    df = pd.DataFrame.from_records(
        research_predictions.values()
    )
    model = load_ml_model('catboost_best_model_2.cbm')
    df['store_nbr'] = df['store_code']
    df['FG+'] = df['FG_plus']
    return get_shap_top_features(model, df[model.feature_names_])[0]
