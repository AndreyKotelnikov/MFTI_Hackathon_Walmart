import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt
from ydata_profiling import ProfileReport
import holidays

# 1. Загрузка данных
def load_data():
    sales = pd.read_csv('data_input/train.csv', parse_dates=['date'])
    weather = pd.read_csv('data_input/weather.csv', parse_dates=['date'])
    key = pd.read_csv('data_input/key.csv')
    data = (
        sales
          .merge(key,     on='store_nbr')
          .merge(weather, on=['station_nbr','date'])
    )
    # Сохраняем в файл
    data.to_csv('clean_data/merged_data.csv', index=False)

    return data

# Создание отчёта
def create_report(data, version):
    # Фикс типов перед генерацией отчёта
    data = data.copy()

    # Исправляем int32/int8 → int64
    int_cols = data.select_dtypes(include=['int32', 'int8']).columns
    data[int_cols] = data[int_cols].astype('int64')

    profile = ProfileReport(data, title='Pandas Profiling Report', explorative=True)
    profile.to_file(f"data/weather{version}.html")

# Загрузка данных из файла
# список бинарных колонок, которые могут принимать только 0 или 1
BINARY_COLS = [
    'BCFG','BLDU','BLSN','BR','DU','DZ','FG','FG+','FU','FZDZ','FZFG',
    'FZRA','GR','GS','HZ','MIFG','PL','PRFG','RA','SG','SN','SQ','TS',
    'TSRA','TSSN','UP','VCFG','VCTS'
]
def load_data_from_file(path: str) -> pd.DataFrame:
    """Загрузить CSV и привести date к datetime."""
    dtype_spec = {col: 'boolean' for col in BINARY_COLS}
    df = pd.read_csv(path, dtype=dtype_spec, low_memory=False)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Заменить метки:
      - 'M' или 'm' → NaN (пропущенные),
      - 'T' или 't' → 0 (trace-показатели осадков)
    и сконвертировать в float/int.
    """
    # глобальные замены
    df = df.replace({'M': np.nan, 'm': np.nan, 'T': 0, 't': 0})

    # список всех столбцов, которые нужно конвертнуть
    numeric_cols = [
        'store_nbr', 'item_nbr', 'units', 'station_nbr',
        'tmax', 'tmin', 'tavg', 'depart', 'dewpoint', 'wetbulb',
        'heat', 'cool', 'snowfall', 'preciptotal',
        'stnpressure', 'sealevel', 'resultspeed', 'resultdir', 'avgspeed'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def fill_missing_average(
    df_base,
    cols=['tavg', 'tmax', 'tmin', 'avgspeed', 'depart', 'dewpoint', 'wetbulb', 'sealevel', 'resultspeed', 'resultdir', 'heat', 'cool'],
    windows=[3, 7, 14, 21, 28]
):
    df = df_base.copy()
    df['day_of_year'] = pd.to_datetime(df['date']).dt.dayofyear
    df = df.sort_values(['station_nbr', 'date'])
    n_days = 366 if df['day_of_year'].max() > 365 else 365
    print(f"Максимальный день года: {n_days}")

    filled_logs = []

    # Для каждой станции и дня года предрасчитываем средние по окну для всех окон
    for col in cols:
        # Копируем пропуски для заполнения
        missing_mask = df[col].isna()
        print(f"Заполнение пропусков в '{col}': {missing_mask.sum()} записей")

        # Предрасчет средних по всем station_nbr и day_of_year для каждого окна
        precomputed = {}
        df_notnull = df[~df[col].isna()]
        for window in windows:
            # Для каждого day_of_year считаем среднее по окну ±window (с учетом перехода)
            means = []
            for doy in range(1, n_days+1):
                # Все day_of_year в окне ±window (с учетом перехода)
                window_doys = np.mod(np.arange(doy - window, doy + window + 1), n_days)
                window_doys[window_doys == 0] = n_days
                # Средние по каждой станции
                mean_vals = (
                    df_notnull[df_notnull['day_of_year'].isin(window_doys)]
                    .groupby('station_nbr')[col]
                    .mean()
                    .reset_index()
                )
                mean_vals['day_of_year'] = doy
                means.append(mean_vals)
            precomputed[window] = pd.concat(means, ignore_index=True)

        # Предрасчет средних по всей станции (на случай если ничего не найдено)
        station_means = (
            df_notnull.groupby('station_nbr')[col]
            .mean()
            .reset_index()
            .rename(columns={col: 'station_mean'})
        )

        # Заполнение пропусков
        idxs = df.index[missing_mask]
        for idx in idxs:
            row = df.loc[idx]
            val = None
            # Пробуем окна по очереди
            for window in windows:
                cur_table = precomputed[window]
                match = cur_table[
                    (cur_table['station_nbr'] == row['station_nbr']) &
                    (cur_table['day_of_year'] == row['day_of_year'])
                ][col]
                if not match.empty and not np.isnan(match.values[0]):
                    val = match.values[0]
                    break
            if val is None:
                # По всей станции
                match = station_means[
                    station_means['station_nbr'] == row['station_nbr']
                ]['station_mean']
                if not match.empty and not np.isnan(match.values[0]):
                    val = match.values[0]
                else:
                    filled_logs.append(
                        f"Нет данных по '{col}' для станции {row['station_nbr']}"
                    )
                    continue
            df.at[idx, col] = val

    if filled_logs:
        unique_logs = set(filled_logs)  # Убираем дубликаты
        print("\n".join(unique_logs))
    df.drop(columns=['day_of_year'], inplace=True)
    return df

def fill_missing_global_average(df, cols=['depart', 'wetbulb', 'sealevel']):
    df = df.copy()
    df['day_of_year'] = pd.to_datetime(df['date']).dt.dayofyear
    n_days = 366 if df['day_of_year'].max() > 365 else 365

    for col in cols:
        # Индексы пропусков
        na_idx = df[df[col].isna()].index
        # Предварительно считаем среднее по всей выборке (если ничего не найдено)
        global_mean = df[col].mean()
        # Предварительно считаем среднее по каждому дню года
        doy_means = df.groupby('day_of_year')[col].mean()

        for idx in na_idx:
            doy = df.at[idx, 'day_of_year']
            val = doy_means.get(doy, np.nan)
            found = False

            # Если не найдено, расширяем окно ±N дней
            for window in [7, 14, 21, 28]:
                if not np.isnan(val):
                    found = True
                    break
                # Все day_of_year в окне ±window с учетом перехода
                doys = np.mod(np.arange(doy-window, doy+window+1), n_days)
                doys[doys == 0] = n_days  # чтобы 0 стал 365
                mask = df['day_of_year'].isin(doys)
                val_window = df.loc[mask, col].mean()
                if not np.isnan(val_window):
                    val = val_window
                    found = True
                    break

            if not found or np.isnan(val):
                # Если всё ещё не найдено — берём глобальное среднее
                val = global_mean

            df.at[idx, col] = val

    df.drop(columns=['day_of_year'], inplace=True)
    return df

def fill_missing_zeros(df_base):
    """Заполнение пропусков подходящими значениями."""
    df = df_base.copy()
    # Заполняем нулями
    df['snowfall'] = df['snowfall'].fillna(0)
    df['preciptotal'] = df['preciptotal'].fillna(0)

    return df

def fill_forward_with_next_non_null(df, cols=None, id_cols=['store_nbr', 'item_nbr'], date_col='date'):
    """
    Для указанных столбцов заполняет пропуски следующим (по дате) непустым значением для того же id.
    """
    if cols is None:
        cols = [
            'max_temp_last_3_days', 'avg_temp_last_3_days',
            'avg_precip_last_3_days', 'avg_sealevel_last_3_days', 'avg_speed_last_3_days',
            'zero_sales_count_7d', 'rolling_sales_mean_3d', 'rolling_sales_mean_7d',
        ]
    df = df.copy()
    df = df.sort_values(id_cols + [date_col], ascending=[True, True, True])  # сортировка по id и дате
    # Для каждого id — применять fillna(method='bfill') (backward fill)
    for col in cols:
        df[col] = df.groupby(id_cols)[col].apply(lambda x: x.bfill()).reset_index(drop=True)
    return df


# Удаляем неинформативные столбцы, например, stnpressure
def drop_useless_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Удалить неинформативные столбцы.
    """
    useless_cols = ['stnpressure', 'sunrise', 'sunset']
    df.drop(columns=useless_cols, inplace=True)
    return df

def encode_codesum(df: pd.DataFrame) -> pd.DataFrame:
    """
    Разбить codesum на бинарные признаки для каждого уникального кода.
    """
    # получаем «one‑hot» по пробелу
    dummies = df['codesum'].fillna('').str.get_dummies(sep=' ')
    # если вдруг появилась колонка '' — удаляем
    if '' in dummies.columns:
        dummies.drop(columns=[''], inplace=True)
    df = pd.concat([df, dummies], axis=1)
    df.drop(columns=['codesum'], inplace=True)
    return df

# Давляем признак id — дуплет, представляющий store_nbr и item_nbr. Например, "2_1" представляет магазин 2, товар 1.
def create_id(df: pd.DataFrame) -> pd.DataFrame:
    """Создаёт id — дуплет, представляющий store_nbr и item_nbr."""
    df['id'] = df['store_nbr'].astype(str) + '_' + df['item_nbr'].astype(str)
    return df

# Удаляем выбросы по units больше 577
def remove_units_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Удаляет выбросы по units больше 577."""
    df = df.copy()
    # Удаляем выбросы по units
    df = df[df['units'] <= 577]
    return df

def remove_zero_sales(df):
    """
    Удалять все нулевые значения нельзя. Часть нулей — это реальное отсутствие продаж.
    Для определения, какие нули следует оставить, нужно использовать следующий подход:
    1. Если для конкретного товара (item_nbr) в конкретном магазине (store_nbr) были стабильные нулевые продажи на протяжении всего периода,
    то это либо отсутствие спроса, либо товар не продавался (его не было в ассортименте).
    Такие записи можно удалить, так как они не несут информации.
    2. Если были нулевые продажи в конкретные дни или периоды, но при этом в другие периоды продажи были,
    такие нули необходимо оставить — это ценная информация о низком или нулевом спросе.
    """
    sales_sum = df.groupby(['store_nbr', 'item_nbr'])['units'].sum()
    zero_sales = sales_sum[sales_sum == 0].index
    df_clean = df[~df.set_index(['store_nbr', 'item_nbr']).index.isin(zero_sales)].copy()
    return df_clean


def preprocess(df, path: str = None) -> pd.DataFrame:
    """Вся цепочка предобработки данных."""
    if path is not None:
        print("Загрузка данных...")
        df = load_data_from_file(path)

    print("Преобразование типов...")
    df = convert_numeric_columns(df)
    print("Заполнение пропусков...")
    df = fill_missing_average(df)
    df = fill_missing_zeros(df)
    df = fill_missing_global_average(df)
    # save to file
    df.to_csv('clean_data/fill_missing_data.csv', index=False)

    print("Преобразование codesum...")
    df = encode_codesum(df)
    df = drop_useless_columns(df)
    df = create_id(df)
    print("Удаление нулевых продаж...")
    df = remove_zero_sales(df)
    df = remove_units_outliers(df)
    return df


def add_time_features(df):
    """Генерация временных признаков на основе даты."""
    # Временные признаки
    df['day_of_week'] = df['date'].dt.strftime('%a').str.lower()  # 3-буквенный код дня
    df['month'] = df['date'].dt.strftime('%b').str.lower()  # 3-буквенный код месяца
    df['weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)

    # Сезоны
    season_map = {
        12: 'winter', 1: 'winter', 2: 'winter',
        3: 'spring', 4: 'spring', 5: 'spring',
        6: 'summer', 7: 'summer', 8: 'summer',
        9: 'autumn', 10: 'autumn', 11: 'autumn'
    }
    df['season'] = df['date'].dt.month.map(season_map)

    # One-hot кодирование
    df = pd.concat([
        df,
        pd.get_dummies(df['day_of_week'], prefix=''),  # mon, tue, wed...
        pd.get_dummies(df['month'], prefix='month'),  # month_jan, month_feb...
        pd.get_dummies(df['season'], prefix='season')  # season_winter...
    ], axis=1)

    # Удаляем оригинальные категориальные столбцы
    df = df.drop(['day_of_week', 'month', 'season'], axis=1)

    # Дополнительные признаки
    df['day_of_year'] = df['date'].dt.dayofyear

    return df


def add_weather_features(df):
    """Генерация погодных признаков."""
    df['temperature_diff'] = df['tmax'] - df['tmin']
    df['heavy_precip'] = (df['preciptotal'].fillna(0).astype(float) > 0.46).astype(int) # 95-th percentile = 0.46

    return df


def add_sales_features(df):
    """Признаки, связанные с магазином и товаром."""
    df['avg_daily_sales_item'] = df.groupby(['store_nbr', 'item_nbr'])['units'].transform('mean')

    store_sales = df.groupby('store_nbr')['units'].sum()
    df['store_sales_rank'] = df['store_nbr'].map(store_sales.rank(method='dense', ascending=False))

    item_sales = df.groupby('item_nbr')['units'].sum()
    df['item_sales_rank'] = df['item_nbr'].map(item_sales.rank(method='dense', ascending=False))
    return df


def add_rolling_weather_features(df):
    """Добавление признаков на основе средних значений за предыдущие 3 дня."""
    df = df.sort_values(by=['station_nbr', 'date'])
    df['max_temp_last_3_days'] = df.groupby('station_nbr')['tmax'].transform(
        lambda x: x.shift(1).rolling(window=3).mean())
    df['avg_temp_last_3_days'] = df.groupby('station_nbr')['tavg'].transform(
        lambda x: x.shift(1).rolling(window=3).mean())
    df['avg_precip_last_3_days'] = df.groupby('station_nbr')['preciptotal'].transform(
        lambda x: x.shift(1).rolling(window=3).mean())
    df['avg_sealevel_last_3_days'] = df.groupby('station_nbr')['sealevel'].transform(
        lambda x: x.shift(1).rolling(window=3).mean())
    df['avg_speed_last_3_days'] = df.groupby('station_nbr')['avgspeed'].transform(
        lambda x: x.shift(1).rolling(window=3).mean())

    return df


def add_holiday_feature(df):
    """Является ли день праздничным в США в период 2012-2014."""
    us_holidays = holidays.US(years=[2012, 2013, 2014])
    # Преобразуем ключи словаря (строки) в datetime64[ns]
    holiday_dates = pd.to_datetime(list(us_holidays.keys()))
    df['is_holiday'] = df['date'].isin(holiday_dates).astype(int)
    return df

def add_zero_sales_count(df, window=7):
    """
    Добавляет признак: количество дней с нулевыми продажами за последние `window` дней.
    Группировка по магазину и товару (store_nbr, item_nbr).
    """
    df = df.sort_values(['store_nbr', 'item_nbr', 'date'])
    # Признак: 1, если продажи нулевые, 0 иначе
    df['zero_sales'] = (df['units'] == 0).astype(int)
    # Скользящее окно: sum за window дней (НЕ включая сегодняшний день, shift(1))
    df['zero_sales_count_7d'] = (
        df.groupby(['store_nbr', 'item_nbr'])['zero_sales']
          .transform(lambda x: x.shift(1).rolling(window, min_periods=1).sum())
    )
    df.drop(columns='zero_sales', inplace=True)
    return df

def add_days_to_nearest_holiday(df, holiday_col='is_holiday', date_col='date'):
    """
    Добавляет признак: дней до ближайшего праздника.
    """
    df = df.sort_values(date_col)
    holidays = pd.to_datetime(df.loc[df[holiday_col] == 1, date_col]).sort_values()
    if holidays.empty:
        df['days_to_nearest_holiday'] = np.nan
        return df

    def nearest_holiday_days(x):
        delta = (holidays - x).abs().dt.days
        return delta.min() if not delta.empty else np.nan

    df['days_to_nearest_holiday'] = pd.to_datetime(df[date_col]).apply(nearest_holiday_days)
    return df


def add_rolling_sales_means(df, windows=[3, 7]):
    """
    Добавляет скользящие средние продаж за последние N дней для каждого окна из windows.
    Группировка по магазину и товару.
    """
    df = df.sort_values(['store_nbr', 'item_nbr', 'date'])
    for w in windows:
        df[f'rolling_sales_mean_{w}d'] = (
            df.groupby(['store_nbr', 'item_nbr'])['units']
              .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
        )
    return df



def add_features(df):
    """Объединение всех этапов добавления признаков, кроме продаж"""
    df = add_time_features(df)
    df = add_weather_features(df)
    df = add_rolling_weather_features(df)
    df = add_holiday_feature(df)
    df = add_sales_features(df)
    df = add_zero_sales_count(df, window=7)
    df = add_days_to_nearest_holiday(df, holiday_col='is_holiday', date_col='date')
    df = add_rolling_sales_means(df, windows=[3, 7])
    df = fill_forward_with_next_non_null(df)
    return df

def plot_missing_for_group(group, date_range):
    group = group.set_index('date')
    # Создаём фрейм для диапазона дат: 1, если дата есть, 0 — пропуск
    idx = pd.DataFrame(index=date_range)
    idx['present'] = 0
    idx.loc[group.index, 'present'] = 1
    # Визуализация: по оси X — даты, по Y — только одна строка
    plt.figure(figsize=(15, 1))
    sns.heatmap([idx['present']], cmap='coolwarm', cbar=True, xticklabels=False)
    title = f"store {group['store_nbr'].iloc[0]}, item {group['item_nbr'].iloc[0]}"
    plt.title(title)
    plt.yticks([])
    plt.show()


import pandas as pd
import numpy as np


def fill_missing_dates(
    df,
    date_col='date',
    group_cols=['store_nbr', 'item_nbr'],
    bin_features=None,
    other_features=None
):
    """
    Заполняет пропущенные даты для каждой группы (store_nbr, item_nbr) в датафрейме df.
    Для каждой пропущенной даты добавляет строку:
      - Числовые признаки (other_features): среднее между ближайшими по времени соседями.
      - Бинарные признаки (bin_features): 0.
      - Для столбцов store_nbr, item_nbr, station_nbr, id — значение из следующей записи (next_row) по дате.
      - Если нет более ранней или более поздней даты для интерполяции — дата пропускается.
    Итоговый датафрейм содержит оригинальные и сгенерированные строки (с признаком filled).
    """

    # Копируем исходный датафрейм, чтобы не менять его напрямую
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    # Если не указаны бинарные признаки, определяем их автоматически (bool/0/1)
    if bin_features is None:
        bin_features = [
            col for col in df.columns
            if df[col].dropna().isin([0, 1]).all() or df[col].dtype == bool
        ]
    # Если не указаны числовые признаки, определяем их автоматически
    if other_features is None:
        exclude = set(group_cols + [date_col] + bin_features)
        other_features = [
            col for col in df.columns
            if col not in exclude and pd.api.types.is_numeric_dtype(df[col])
        ]

    # Список колонок, которые нужно копировать из next_row
    copy_from_next = ['store_nbr', 'item_nbr', 'station_nbr', 'id']
    # Оставляем только те, которые реально есть в датафрейме
    copy_from_next = [col for col in copy_from_next if col in df.columns]

    filled_rows = []  # Здесь будут собираться новые строки с заполнениями
    # Общий диапазон дат (по всем данным)
    all_dates = pd.date_range(df[date_col].min(), df[date_col].max())

    # Проходим по каждой уникальной группе store_nbr, item_nbr
    for group, group_df in df.groupby(group_cols):
        group_df = group_df.sort_values(date_col)
        group_dates = set(group_df[date_col])
        # Список дат, которых не хватает в группе
        missing_dates = [d for d in all_dates if d not in group_dates]
        for d in missing_dates:
            # Ищем ближайшие строки с датами до и после пропуска
            prev = group_df[group_df[date_col] < d]
            next_ = group_df[group_df[date_col] > d]
            if prev.empty or next_.empty:
                continue  # Если нет "до" или "после", пропуск не заполняем
            prev_row = prev.iloc[-1]
            next_row = next_.iloc[0]
            # Начальные значения: группы по умолчанию (можно переписать ниже)
            new_row = {col: val for col, val in zip(group_cols, group)}
            new_row[date_col] = d
            # Для специальных колонок копируем из следующей записи next_row
            for col in copy_from_next:
                new_row[col] = next_row[col]
            # Для числовых признаков — усреднение между ближайшими датами
            for col in other_features:
                v1, v2 = prev_row[col], next_row[col]
                new_row[col] = np.nan if pd.isnull(v1) or pd.isnull(v2) else (v1 + v2) / 2
            # Для бинарных признаков — всегда 0
            for col in bin_features:
                new_row[col] = 0
            # Признак, что эта строка была сгенерирована, а не исходная
            new_row['filled'] = True
            filled_rows.append(new_row)

    # Объединяем оригинальный датафрейм и новые строки, сортируем по группе и дате
    out = pd.concat(
        [df.assign(filled=False), pd.DataFrame(filled_rows)],
        ignore_index=True
    ).sort_values(group_cols + [date_col]).reset_index(drop=True)
    return out

# Отображение пропущенных дней
def show_missing_dates(df):
    # Сортируем
    df = df.sort_values(['store_nbr', 'item_nbr', 'date'])

    # Для ускорения вычислим полный диапазон дат (для всех групп)
    full_date_range = pd.date_range(df['date'].min(), df['date'].max())

    matrix = []
    labels = []
    for (store, item), group in df.groupby(['store_nbr', 'item_nbr']):
        idx = pd.Series(0, index=full_date_range)
        idx.loc[group['date']] = 1
        matrix.append(idx.values)
        labels.append(f'{store}-{item}')

    plt.figure(figsize=(15, len(matrix) // 2))
    sns.heatmap(matrix, cmap='coolwarm', cbar=True)
    plt.yticks(ticks=[i + 0.5 for i in range(len(labels))], labels=labels, rotation=0)
    plt.xlabel('Дни')
    plt.title('Пропуски по дням для каждой группы store-item')
    plt.show()

def show_only_missing_dates(df):
    # Сортируем по группе и дате
    df = df.sort_values(['store_nbr', 'item_nbr', 'date'])

    # Получаем общий диапазон дат
    full_date_range = pd.date_range(df['date'].min(), df['date'].max())

    matrix = []
    labels = []

    for (store, item), group in df.groupby(['store_nbr', 'item_nbr']):
        idx = pd.Series(0, index=full_date_range)
        idx.loc[group['date']] = 1
        # Проверяем: если в группе есть хотя бы один пропуск (т.е. есть нули)
        if (idx == 0).any():
            matrix.append(idx.values)
            labels.append(f'{store}-{item}')

    if not matrix:
        print("Нет групп с пропусками по дням.")
        return

    plt.figure(figsize=(15, max(2, len(matrix) // 2)))
    sns.heatmap(matrix, cmap='coolwarm', cbar=True)
    plt.yticks(ticks=[i + 0.5 for i in range(len(labels))], labels=labels, rotation=0)
    plt.xlabel('Дни')
    plt.title('Пропуски по дням для каждой группы store-item (только группы с пропусками)')
    plt.show()



if __name__ == '__main__':
    data = load_data()
    df = preprocess(data)
    df.to_csv('clean_data/processed_data.csv', index=False) # Осталось 5% от данных: 236036 вместо 4617600
    df = fill_missing_dates(df, date_col='date', group_cols=['store_nbr', 'item_nbr'])
    df = add_features(df)
    df.to_csv('clean_data/data_add_features.csv', index=False)
    numerical_features =df.select_dtypes(include=['number']).columns.tolist()
    # # Проверка количества пропусков
    print("Пропуски:")
    print(df[numerical_features].isna().sum())
    show_missing_dates(df)
    show_only_missing_dates(df)

    df.to_csv('clean_data/data_clean.csv', index=False)
    create_report(df, 2)




