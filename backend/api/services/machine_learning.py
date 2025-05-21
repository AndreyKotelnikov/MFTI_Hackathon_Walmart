import os
import json
from decimal import Decimal
from catboost import Pool
import pandas as pd
from hackathon.sources_db import runQuery
from catboost import CatBoostClassifier
from django.conf import settings


MODELS_FEATURES_TRANSLATION = {
    'city_size': 'Размер города покупателя',
    'city_center_distance_km': 'Удалённость покупателя от центра города',
    'city_center_level': 'Удалённость покупателя от центра города (относительная)',
    'days_after_order': 'Количество дней, прошедшее после последней покупки',
    'state_income': 'Средний доход по штату',
    'last_delivery_distance_km': 'Дальность последней доставки в километрах',
    'last_delivery_cost': 'Цена последней доставки',
    'last_order_cost': 'Цена последней покупки',
    'last_review_score': 'Оценка в последнем отзыве',
    'last_review_length': 'Длина последнего отзыва',
    'last_review_product_state': 'Состояние продукта по последнему отзыву (NLP анализ)',
    'last_review_sentiment': 'Настроение клиента по последнему отзыву (NLP анализ)',
    'avg_order_interval_days': 'Средний интервал между прошлыми покупками',
    'main_payment_type': 'Основной способ оплаты',
    'last_order_day_of_year': 'Номер дня в году для последнего ордера (учёт сезонности)',
    'percent_null_reviews': 'Доля продаж без отзыва у продавца',
    'dispersion_review_score': 'Дисперсия оценки отзывов продавца',
    'avg_review_message_length': 'Средняя длина отзывов у продавца',
    'product_count': 'Количество продуктов у продавца',
    'order_date_variance': 'Дисперсия продаж у продавца',
    'product_name_lenght': 'Длина названия последнего купленного продукта',
    'product_description_lenght': 'Длина описания последнего купленного продукта',
    'product_photos_qty': 'Количество фотографий у последнего купленного продукта',
    'previos_orders_count': 'Количество ордеров в прошлом'
}

def get_customer_xdata(customer_unique_id):
    customer_features_current = runQuery(f"""
SELECT
  cft.id as cft_id,
  cft.*,
  cft.days_before_order < 30 as is_customer_will_month,
  srm.*,
  p.*
FROM customer_features_current cft
left join orders o on o.order_id::uuid=cft.order_id 
inner join orders_items oi on oi.order_id =o.order_id
left join seller_retention_metrics srm on srm.seller_id =oi.seller_id
left join products p on p.product_id =oi.product_id
where cft.customer_unique_id='{customer_unique_id}' and cft.id is not null""")
    return pd.DataFrame(customer_features_current)

def normalize_customer_xdata(mlmodel, customer_features):
    customer_features['main_payment_type'] = customer_features['main_payment_type'].fillna('not_defined')
    X = customer_features[mlmodel.feature_columns]
    X = X.fillna(value=mlmodel.mean_values_json)
    return X

def load_ml_model(filename):
    model = CatBoostClassifier()
    fullpath = os.path.join(settings.MEDIA_ROOT, 'ml-models', filename)
    model.load_model(fullpath)
    return model

def get_predict_interpretation(model: CatBoostClassifier, X: pd.DataFrame):

    cat_features=['main_payment_type', 'customer_state']
    cat_features = [col for col in cat_features if col in X.columns]
    sample_pool = Pool(X, cat_features=cat_features)

    # Получаем SHAP-значения (последний столбец — это base value)
    shap_values = model.get_feature_importance(
        type='ShapValues',
        data=sample_pool
    )

    result = []
    for shap_value in shap_values:
        # Берём первую (и единственную) строку и убираем base value
        shap_importances = pd.Series(shap_value[:-1], index=X.columns)
        shap_importances = shap_importances.abs().sort_values(ascending=False)

        top_5_shap = shap_importances.head(5)
        items = top_5_shap.to_dict()
        interpretation = get_xdata_properties(items)
        result.append(interpretation)
    return result

def get_xdata_properties(items: dict):
    properties = []
    for key in items:
        name = MODELS_FEATURES_TRANSLATION[key] if key in MODELS_FEATURES_TRANSLATION else key
        value = items[key]
        properties.append({
            'key': key,
            'name': name,
            'value': value
        })
    return properties
    