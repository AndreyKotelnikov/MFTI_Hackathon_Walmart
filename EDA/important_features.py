import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Загрузка данных
def load_data(path: str) -> pd.DataFrame:
    """Загружает данные из CSV и преобразует дату."""
    df = pd.read_csv(path, parse_dates=['date'])
    return df

# Подготовка данных
def prepare_data(df: pd.DataFrame) -> (pd.DataFrame, pd.Series):
    """Отбирает данные по id и отделяет целевую переменную."""
    y = df['units']
    X = df.drop(['units', 'date'], axis=1)  # id/date не используем как признаки
    main_features = [
        # основные погодные признаки, праздничные, день недели, сезон
        'tmax', 'tavg', 'depart',
        'dewpoint',
        'preciptotal',
        'sealevel',
        'avgspeed',
        # бинарные погодные признаки
        'RA', 'SN',
        # сезонные и праздничные признаки
        'weekend', 'day_of_year', 'days_to_nearest_holiday',
        'store_nbr',
        'item_nbr',
        'station_nbr'
    ]

    X = X[main_features]
    cat_features = [
        'store_nbr',
        'item_nbr',
        'station_nbr'
    ]
    for col in cat_features:
        if col in X.columns:
            X[col] = X[col].astype(str)

    # Все бинарные/булевы — в int
    for col in X.columns:
        if X[col].dtype == 'bool':
            X[col] = X[col].astype(int)
        elif X[col].dtype == 'object':
            # Преобразуем True/False к 1/0 если это бинарный признак
            uniq = set(X[col].unique())
            if uniq <= {'True', 'False', True, False, '0', '1', 0, 1}:
                X[col] = X[col].map({'True': 1, 'False': 0, True: 1, False: 0, '0': 0, '1': 1, 0: 0, 1: 1})

    # Разбиваем по дате: последние N% на тест
    split_date = df['date'].quantile(0.8)
    X_train = X[df['date'] <= split_date]
    y_train = y[df['date'] <= split_date]
    X_test = X[df['date'] > split_date]
    y_test = y[df['date'] > split_date]

    return X_train, y_train, X_test, y_test, cat_features

# Обучение модели
def train_model(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, cat_features: list):
    """Инициализация и обучение CatBoost модели."""
    model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.03,
        depth=8,
        cat_features=cat_features,
        eval_metric='RMSE',
        early_stopping_rounds=50,
        verbose=100
    )

    model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        use_best_model=True
    )

    return model

# Оценка качества модели
def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series):
    """Оценка качества модели на тестовых данных."""
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"R2: {r2:.3f}")

    return rmse, mae, r2



# Получить важность признаков
def get_feature_importance(model, X: pd.DataFrame, id: str) -> pd.DataFrame:
    """Получить важность признаков из обученной модели."""
    feature_importances = model.get_feature_importance()
    feature_names = X.columns

    # Собрать в DataFrame и отсортировать
    fi_df = pd.DataFrame({
        'feature': feature_names,
        'importance': feature_importances
    }).sort_values('importance', ascending=False)

    # Вывести топ-20
    # print(fi_df.head(20))
    # Сохраняем в CSV
    # fi_df.to_csv(f'important_features/feature_importance_{id}.csv', index=False)

    return fi_df

# Основной код
if __name__ == "__main__":
    # Загрузка данных
    df = load_data('clean_data/data_clean.csv')

    # Список для метрик по всем id
    metrics_list = []
    fi_dict = {}  # id -> {feature: importance}
    all_top_features = set()
    # id_list = ['26_2', '35_16']  # если нужно только по этим id
    # df_selected = df[df['id'].isin(id_list)]
    # Группировка по id
    for id_val, group in df.groupby('id'):
        # Не менее 30 точек, иначе CatBoost может не обучиться
        if len(group) < 30:
            continue

        # Подготовка данных (доработайте prepare_data, чтобы принимать df для одной группы)
        X_train, y_train, X_test, y_test, cat_features = prepare_data(group)

        # Метрики по тренировочной выборке (train)
        day_not_zero_unit_count = (y_train > 0).sum()
        day_not_zero_unit_percent = (day_not_zero_unit_count / len(y_train) * 100) if len(y_train) > 0 else 0.0

        # Если все значения в y_train или y_test одинаковые, пропускаем, фиксируя в метриках 0
        if y_train.nunique() <= 1 or y_test.nunique() <= 1:
            metrics_list.append({
                'id': id_val,
                'rmse': 0.0,
                'r2': 0.0,
                'unit_max': y_train.max(),
                'unit_mean': y_train.mean(),
                'day_not_zero_unit_count': day_not_zero_unit_count,
                'day_not_zero_unit_percent': day_not_zero_unit_percent
            })
            continue

        # Иногда после разбиения тест пустой (редко, но бывает)
        if len(X_test) == 0 or len(X_train) == 0:
            continue

        # Обучение
        model = train_model(X_train, y_train, X_test, y_test, cat_features)

        # Оценка качества
        rmse, mae, r2 = evaluate_model(model, X_test, y_test)

        # Сохраняем id и метрики
        metrics_list.append({
            'id': id_val,
            'rmse': round(rmse, 3),
            'r2': round(r2, 3),
            'unit_max': y_train.max(),
            'unit_mean': y_train.mean(),
            'day_not_zero_unit_count': day_not_zero_unit_count,
            'day_not_zero_unit_percent': day_not_zero_unit_percent
        })

        # Получаем важность признаков
        fi_df = get_feature_importance(model, X_train, str(id_val))
        top_features = fi_df.head(10)
        fi_dict[id_val] = dict(zip(top_features['feature'], top_features['importance']))
        all_top_features.update(top_features['feature'])

    # Формируем итоговую таблицу
    metrics_df = pd.DataFrame(metrics_list)

    # Сортируем по r2 (сначала максимальные)
    metrics_df = metrics_df.sort_values('r2', ascending=False).reset_index(drop=True)

    # Сохраняем в CSV
    metrics_df.to_csv('important_features/metrics_catboost.csv', index=False)

    # Таблица с важностями признаков
    all_top_features = list(all_top_features)
    fi_table = pd.DataFrame(0.0, index=metrics_df['id'], columns=all_top_features)
    for id_val in fi_dict:
        for feat, importance in fi_dict[id_val].items():
            fi_table.at[id_val, feat] = round(importance, 3)

    # Сортировка столбцов по убыванию суммы важностей
    cols_sorted = fi_table.sum(axis=0).sort_values(ascending=False).index
    fi_table = fi_table[cols_sorted]
    # Строки уже идут в порядке id из metrics_df

    fi_table.to_csv('important_features/feature_importance_by_id.csv')

    # Определим список колонок для метрик и рассчитаем ширины
    metrics_columns = ['index', 'id', 'rmse', 'r2', 'unit_max', 'unit_mean', 'day_not_zero_unit_count', 'day_not_zero_unit_percent']
    metrics_data = metrics_df.copy()
    metrics_data = metrics_data.reset_index(drop=True)
    metrics_data.insert(0, 'index', metrics_data.index)  # добавим индекс как первый столбец

    # Для каждого столбца вычисляем оптимальную ширину
    metrics_col_widths = {}
    for col in metrics_columns:
        max_val_len = metrics_data[col].astype(str).map(len).max() if col in metrics_data else 0
        metrics_col_widths[col] = max(len(col) + 2, max_val_len + 2, 10)

    # Формируем заголовок
    metrics_header = "".join([f"{col:>{metrics_col_widths[col]}}" for col in metrics_columns])
    print(metrics_header)
    print("=" * len(metrics_header))

    # Формируем строки (первые 20)
    for idx, row in metrics_data.head(20).iterrows():
        line = (
            f"{row['index']:>{metrics_col_widths['index']}}"
            f"{str(row['id']):>{metrics_col_widths['id']}}"
            f"{row['rmse']:>{metrics_col_widths['rmse']}.3f}"
            f"{row['r2']:>{metrics_col_widths['r2']}.3f}"
            f"{row['unit_max']:>{metrics_col_widths['unit_max']}}"
            f"{row['unit_mean']:>{metrics_col_widths['unit_mean']}.3f}"
            f"{row['day_not_zero_unit_count']:>{metrics_col_widths['day_not_zero_unit_count']}}"
            f"{row['day_not_zero_unit_percent']:>{metrics_col_widths['day_not_zero_unit_percent']}.2f}%"
        )
        print(line)
    print("\n"* 2)

    # Формируем ширины для каждого признака
    col_widths = {col: max(len(str(col)) + 2, 10) for col in fi_table.columns}

    # Заголовок
    header = f"{'index':>6} {'id':>12} " + "".join([f"{col:>{col_widths[col]}}" for col in fi_table.columns])
    print(header)
    print("=" * len(header))

    # Данные по строкам (первые 20)
    for idx, (id_val, row) in enumerate(fi_table.iterrows()):
        if idx >= 20:
            break
        line = f"{idx:6} {id_val:>12} " + "".join([f"{row[col]:>{col_widths[col]}.3f}" for col in fi_table.columns])
        print(line)



