import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.api import anova_lm
from scipy import stats  # Для теста Шапиро-Уилка


def calculate_vif(X, vif_threshold=10, corr_threshold=0.9):
    """Вычисляет VIF, находит группы коллинеарных признаков и оставляет по одному из группы"""
    features = X.columns.tolist()

    # Удаление константных признаков
    constant_cols = [col for col in features if X[col].nunique() == 1]
    X = X.drop(columns=constant_cols, errors='ignore')

    # Удаление идеально коррелированных признаков
    corr_matrix = X.corr().abs()
    perfect_corr = np.where(corr_matrix == 1.0)
    perfect_pairs = [(corr_matrix.index[x], corr_matrix.columns[y])
                     for x, y in zip(*perfect_corr) if x != y]
    to_drop = list({pair[1] for pair in perfect_pairs})
    X = X.drop(columns=to_drop, errors='ignore')

    features = X.columns.tolist()
    corr_matrix = X.corr().abs()

    # Находим группы высококоррелированных признаков
    clusters = []
    visited = set()

    for i in range(len(features)):
        if features[i] in visited:
            continue
        cluster = [features[i]]
        visited.add(features[i])

        # Ищем все признаки с корреляцией > порога
        for j in range(i + 1, len(features)):
            if corr_matrix.loc[features[i], features[j]] > corr_threshold:
                cluster.append(features[j])
                visited.add(features[j])

        if len(cluster) > 1:
            clusters.append(cluster)

    # Удаляем признаки из групп, оставляя по одному
    to_drop = []
    for cluster in clusters:
        print(f"\nГруппа коллинеарных признаков: {cluster}")

        # Вычисляем VIF для всех признаков в группе
        vifs = {}
        for feature in cluster:
            if feature in X.columns:
                vif = variance_inflation_factor(X.values, X.columns.get_loc(feature))
                vifs[feature] = vif

        # Критерий выбора: признак с наименьшим VIF,
        # если VIF < порога, иначе с наибольшей дисперсией
        valid_features = [f for f in cluster if f in X.columns]
        if not valid_features:
            continue

        # Сортируем по VIF и дисперсии
        sorted_features = sorted(
            valid_features,
            key=lambda x: (
                vifs[x] if vifs[x] < vif_threshold else np.inf,
                -X[x].var()
            )
        )

        # Оставляем лучший признак
        keep_feature = sorted_features[0]
        print(f"Оставляем: {keep_feature} (VIF={vifs[keep_feature]:.2f}, var={X[keep_feature].var():.2f})")

        # Собираем признаки на удаление
        to_drop.extend([f for f in cluster if f != keep_feature and f in X.columns])

    # Удаляем признаки из групп
    X_reduced = X.drop(columns=to_drop, errors='ignore')

    # Дополнительная проверка VIF для оставшихся признаков
    print("\nФинальная проверка VIF:")
    vifs = pd.DataFrame()
    vifs["feature"] = X_reduced.columns
    vifs["VIF"] = [variance_inflation_factor(X_reduced.values, i) for i in range(X_reduced.shape[1])]
    print(vifs.sort_values("VIF", ascending=False))

    return X_reduced


def compare_models(full_model, restricted_model, alpha=0.05):
    """Сравнение моделей с помощью F-теста и AIC/BIC"""
    # F-тест
    anova_res = anova_lm(restricted_model, full_model)
    p_value = anova_res['Pr(>F)'][1]

    # AIC/BIC сравнение
    aic_diff = full_model.aic - restricted_model.aic
    bic_diff = full_model.bic - restricted_model.bic

    return {
        'f_test_pass': p_value < alpha,
        'aic_better': aic_diff < 0,
        'bic_better': bic_diff < 0,
        'p_value': p_value
    }

df = pd.read_csv('data/data_clean.csv', parse_dates=['date'])

file_coef_path = 'stats/significant_features.txt'
p_value_threshold = 0.05
coef_threshold = 0.01
results = []
ids = df['id'].unique().tolist()
ids = sorted(ids, key=lambda x: tuple(map(int, x.split('_'))))
count = 0

# Сначала определим все возможные фичи для единой структуры
all_possible_features = df.columns.difference([
    'id', 'date', 'store_nbr', 'item_nbr', 'units','station_nbr',
    'wetbulb',
    'daylight_duration'

]).tolist()

# Только погодные признаки
weather_features = [
    'tmax', 'tmin',
    'tavg', 'depart', 'dewpoint',
    # 'wetbulb' Слабопонятный признак для меня
    'heat', 'cool',
    'snowfall', 'preciptotal', 'sealevel',
    'resultspeed',
    'resultdir',
    'avgspeed', 'BCFG', 'BLDU', 'BLSN', 'BR', 'DU', 'DZ', 'FG', 'FG+', 'FU',
    'FZDZ', 'FZFG', 'FZRA', 'GR', 'GS', 'HZ', 'MIFG', 'PL', 'PRFG', 'RA',
    'SG', 'SN', 'SQ', 'TS', 'TSRA', 'TSSN', 'UP', 'VCFG', 'VCTS',
    'temperature_diff', 'heavy_precipitation', 'avg_temp_last_3_days',
    'avg_precip_last_3_days', 'avg_sealevel_last_3_days', 'avg_speed_last_3_days',
    # 'daylight_duration' Косвенно указывает на сезонность
]

# Удаляем файл, если он существует
if os.path.exists(file_coef_path):
    os.remove(file_coef_path)

results = []  # Здесь будем хранить словари с результатами
all_weather_coefs = set()  # Множество всех найденных признаков

for id_group in ids:
    subset = df[df['id'] == id_group].copy()
    # Преобразование типов
    subset = subset.replace([np.inf, -np.inf], np.nan)
    for col in subset.columns:
        if subset[col].dtype == object:
            subset[col] = pd.to_numeric(subset[col], errors='coerce')
    subset = subset.fillna(0)

    # Фильтрация числовых колонок
    numeric_cols = subset.select_dtypes(include=[np.number]).columns
    subset = subset[numeric_cols]

    non_numeric_cols = subset.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric_cols:
        print(f"\n[DEBUG] Нечисловые колонки для id {id_group} после фильтрации:")
        print(non_numeric_cols)

    if len(subset) < 10:
        print(f"Недостаточно данных для id {id_group} ({len(subset)}), пропускаем...")
        continue

    # Удаление константных признаков
    numeric_cols = subset.select_dtypes(include=[np.number]).columns
    constant_cols = [col for col in numeric_cols if subset[col].nunique() == 1]
    subset = subset.drop(columns=constant_cols)

    # Разделение на погодные и непогодные признаки
    all_features = subset.columns.intersection(all_possible_features).tolist()
    weather_feats = [f for f in all_features if f in weather_features]
    non_weather_feats = [f for f in all_features if f not in weather_features]

    if not weather_feats:
        continue

    try:
        # Полная модель с погодными признаками
        X_full = subset[all_features]
        X_full = calculate_vif(X_full)  # Удаление мультиколлинеарных признаков
        X_full = sm.add_constant(X_full)
        y = subset['units']
        model_full = sm.OLS(y, X_full).fit()

        # Проверка остатков
        residuals = model_full.resid
        _, p_normality = stats.shapiro(residuals)
        if p_normality < 0.05:
            print(f"Предупреждение: остатки не нормальны для id {id_group} (p={p_normality:.3f})")

        # Ограниченная модель без погодных признаков
        X_restricted = subset[non_weather_feats]
        if not X_restricted.empty:
            X_restricted = sm.add_constant(X_restricted)
            model_restricted = sm.OLS(y, X_restricted).fit()
        else:
            model_restricted = None

    except Exception as e:
        print(f"Ошибка для id {id_group}: {str(e)}")
        continue

    # Проверка значимости погодных признаков
    weather_results = {}
    if model_restricted:
        comparison = compare_models(model_full, model_restricted)
        if comparison['f_test_pass'] or comparison['aic_better']:
            # Сохраняем только устойчивые погодные признаки
            weather_feats_in_model = [f for f in weather_feats if f in X_full.columns]
            if not weather_feats_in_model:
                print(f"Нет погодных признаков после VIF для {id_group}")
                continue
            # p_value_threshold = 0.05 / len(weather_feats_in_model)  # Bonferroni correction
            for feat in weather_feats_in_model:
                pval = model_full.pvalues[feat]
                coef = model_full.params[feat]
                if pval < p_value_threshold and abs(coef) > coef_threshold:
                    weather_results[feat] = coef
                    all_weather_coefs.add(feat)  # Собираем уникальные признаки

    # Запись результатов
    if weather_results:
        row = {'id': id_group, **weather_results}
        results.append(row)

        res_str = f"{id_group} ({len(subset)}) = " + ", ".join(
            [f"{k}: {v:.2f}" for k, v in weather_results.items()]
        )
        with open(file_coef_path, 'a') as f:
            f.write(res_str + '\n')
        print(res_str)

# Создаем DataFrame
if results:
    df_results = pd.DataFrame(results).set_index('id')

    # Добавляем отсутствующие колонки и заполняем нулями
    for col in all_weather_coefs:
        if col not in df_results.columns:
            df_results[col] = 0.0

    # Удаляем полностью нулевые колонки
    df_results = df_results.loc[:, (df_results != 0).any(axis=0)]

    # Сортируем колонки по частоте встречаемости
    col_freq = df_results.astype(bool).sum().sort_values(ascending=False).index.tolist()
    df_results = df_results[col_freq].reset_index()

    # Сохраняем в файл
    df_results.to_csv('stats/weather_significant_features.csv', index=False)
else:
    print("Нет значимых признаков!")