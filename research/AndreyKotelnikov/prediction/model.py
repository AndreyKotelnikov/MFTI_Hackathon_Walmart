import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

# Для визуализации
import matplotlib.pyplot as plt


def load_and_prepare_data(id_to_predict, lag=7):
    # Загрузка данных
    df = pd.read_csv('data/data_clean.csv', parse_dates=['date'])
    df = df[df['id'] == id_to_predict].sort_values('date')

    # Создание временных лагов
    for i in range(1, lag + 1):
        df[f'units_lag_{i}'] = df['units'].shift(i)

    # Заполнение пропусков
    df = df.fillna(method='ffill').fillna(0)

    # Извлечение значимых погодных признаков
    weather_coefs = pd.read_csv('stats/weather_significant_features.csv')
    weather_cols = weather_coefs[weather_coefs['id'] == id_to_predict].dropna(axis=1).columns.tolist()[1:]

    # Разделение признаков
    base_features = [
        'units_lag_1', 'units_lag_2', 'units_lag_3',
        'weekend', 'is_holiday', 'day_of_year',
        'store_sales_rank', 'item_sales_rank'
    ]

    weather_features = list(set(weather_cols) & set(df.columns))

    return df, base_features, weather_features


def remove_collinear_features(df, features, threshold=0.9):
    corr_matrix = df[features].corr().abs()
    to_drop = set()

    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if corr_matrix.iloc[i, j] > threshold:
                colname = corr_matrix.columns[i]
                to_drop.add(colname)

    return list(set(features) - to_drop)


def train_and_validate(df, features, target='units', n_splits=3):
    X = df[features]
    y = df[target]

    tscv = TimeSeriesSplit(n_splits=n_splits)
    metrics = []
    models = []
    features_list = []  # Сохраняем список используемых признаков

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        # Фильтрация признаков для текущего фолда
        final_features = remove_collinear_features(pd.concat([X_train, X_val]), features)
        X_train_filt = X_train[final_features]
        X_val_filt = X_val[final_features]

        model = lgb.LGBMRegressor(
            n_estimators=1000,
            learning_rate=0.05,
            random_state=42
        )

        model.fit(
            X_train_filt, y_train,
            eval_set=[(X_val_filt, y_val)],
            eval_metric="mae",
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(50)
            ]
        )

        # Сохраняем модель и использованные признаки
        models.append({
            'model': model,
            'features': final_features.copy()
        })

        pred = model.predict(X_val_filt)
        mae = mean_absolute_error(y_val, pred)
        metrics.append(mae)
        print(f'Fold {fold + 1} MAE: {mae:.2f}')

    return models, np.mean(metrics)


def generate_predictions(models, last_data, future_dates):
    predictions = []

    for date in future_dates:
        # Для каждой модели из ансамбля
        fold_preds = []
        for fold_model in models:
            model = fold_model['model']
            features = fold_model['features']

            # Подготовка данных с правильными признаками
            input_data = last_data[features].copy()

            # Прогноз
            pred = model.predict(input_data)[0]
            fold_preds.append(pred)

            # Обновление лагов
            new_data = input_data.copy()
            for i in range(len(features) - 1, 0, -1):
                if features[i].startswith('units_lag_'):
                    lag_num = int(features[i].split('_')[-1])
                    if lag_num == 1:
                        new_data[features[i]] = pred
                    else:
                        prev_lag = features[i - 1]
                        new_data[features[i]] = input_data[prev_lag]

            last_data = new_data  # Обновляем данные для следующей итерации

        predictions.append(np.mean(fold_preds))

    return predictions


def main(id_to_predict='1_51', forecast_days=30):
    # Загрузка данных
    df, base_features, weather_features = load_and_prepare_data(id_to_predict)

    # Обучение моделей
    print('Training base model...')
    base_models, base_mae = train_and_validate(df, base_features)

    print('\nTraining weather model...')
    full_features = base_features + weather_features
    weather_models, weather_mae = train_and_validate(df, full_features)

    # Подготовка данных для прогноза
    last_date = df['date'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(1), periods=forecast_days)

    # Базовый прогноз
    last_data_base = df[base_models[0]['features']].iloc[-1:].copy()
    base_predictions = generate_predictions(base_models, last_data_base, future_dates)

    # Прогноз с погодой
    try:
        weather_features_used = weather_models[0]['features']
        last_data_weather = df[weather_features_used].iloc[-1:].copy()

        # Заполнение погодных данных (пример)
        for feat in weather_features_used:
            if feat.startswith('weather_'):
                last_data_weather[feat] = df[feat].mean()

        weather_predictions = generate_predictions(weather_models, last_data_weather, future_dates)
    except Exception as e:
        print(f"Weather prediction failed: {str(e)}")
        weather_predictions = base_predictions.copy()

    # Визуализация и вывод результатов
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['units'], label='Historical')
    plt.plot(future_dates, base_predictions, label='Base Forecast')
    plt.plot(future_dates, weather_predictions, label='Weather Adjusted')
    plt.title(f'Sales Forecast for {id_to_predict}')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()