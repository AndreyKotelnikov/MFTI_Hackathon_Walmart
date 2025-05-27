import os
import json
from decimal import Decimal
from catboost import Pool
import pandas as pd
from hackathon.sources_db import runQuery
# from catboost import CatBoostClassifier
from django.conf import settings
from django.db import transaction
from api.models import PredictionReal, PredictionResearch, Research
from catboost import CatBoostRegressor, Pool


def load_ml_model(filename):
    model = CatBoostRegressor()
    fullpath = os.path.join(settings.MEDIA_ROOT, 'ml-models', filename)
    model.load_model(fullpath)
    return model


def get_shap_top_features(model, X: pd.DataFrame):
    cat_features = ['store_code', 'store_item_code']  # Пример категориальных фичей
    cat_features = [col for col in cat_features if col in X.columns]
    
    sample_pool = Pool(X, cat_features=cat_features)
    
    # Получаем SHAP-значения (размер: [n_samples, n_features + 1])
    shap_values = model.get_feature_importance(type='ShapValues', data=sample_pool)
    
    result = []
    for shap_row in shap_values:
        # Убираем последний элемент (base value) и берём абсолютные значения
        shap_importances = pd.Series(shap_row[:-1], index=X.columns).abs()
        # Сортируем
        top_features = shap_importances.sort_values(ascending=False).to_dict()
        result.append(top_features)
    
    return result


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
    model = load_ml_model('CatBoost v1.cbm')
    df['units_pred'] = model.predict(df[model.feature_names_])
    
    # Обновляем объекты PredictionResearch
    with transaction.atomic():
        for _, row in df.iterrows():
            prediction = research_predictions.get(id=row['id'])
            real_units_pred = prediction.real.units_pred if hasattr(prediction.real, 'units_pred') else 0
            
            prediction.units_pred = row['units_pred'] if row['units_pred'] >= 0 else 0
            
            # Вычисляем разницу и коэффициент
            prediction.difference = row['units_pred'] - real_units_pred
            prediction.coefficient = row['units_pred'] / real_units_pred if real_units_pred != 0 else 0
            
            prediction.save()
            print('3.3')
    
    return research_predictions


def get_prediction_shap(prediction_id):
    research_predictions = PredictionResearch.objects.filter(id=prediction_id).select_related('real')
    df = pd.DataFrame.from_records(
        research_predictions.values()
    )
    model = load_ml_model('CatBoost v1.cbm')
    return get_shap_top_features(model, df[model.feature_names_])[0]
