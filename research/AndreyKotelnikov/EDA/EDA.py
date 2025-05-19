import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt
from ydata_profiling import ProfileReport
import holidays

# 1. Загрузка данных
def load_data():
    sales = pd.read_csv('data/train.csv', parse_dates=['date'])
    weather = pd.read_csv('data/weather.csv', parse_dates=['date'])
    key = pd.read_csv('data/key.csv')
    data = (
        sales
          .merge(key,     on='store_nbr')
          .merge(weather, on=['station_nbr','date'])
    )
    # Сохраняем в файл
    data.to_csv('data/merged_data.csv', index=False)

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
    dtype_spec = {col: 'uint8' for col in BINARY_COLS}
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


def convert_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Преобразует столбцы sunrise/sunset:
    1. Заменяет '-' на NaN
    2. Конвертирует строки в числа
    3. Переводит формат HHMM в общее количество минут
    """
    for col in ['sunrise', 'sunset']:
        # Замена '-' на NaN и конвертация в число
        df[col] = df[col].replace('-', np.nan)
        df[col] = pd.to_numeric(df[col], errors='coerce')

        # Преобразование HHMM в минуты
        df[col] = (df[col] // 100) * 60 + (df[col] % 100)

    return df

# Заполняем NAN в столбцах tavg, tmax, tmin, preciptotal, sealevel и другие средним значением по станции и по ближайшим ненулевым значениям на даты до и после
def fill_weather_nan(df):
    """Заполнение NAN в столбцах погоды по станции и интерполяцией."""
    df = df.copy()
    df = df.sort_values(['station_nbr', 'date'])
    for col in ['tavg', 'tmax', 'tmin', 'sealevel', 'avgspeed', 'depart', 'sunrise', 'sunset']:
        # интерполируем линейно между ближайшими датами
        df[col] = df.groupby('station_nbr')[col].transform(
            lambda x: x.interpolate(method='linear', limit_direction='both')
        )
        # оставшиеся NaN заполняем средним по станции
        df[col] = df.groupby('station_nbr')[col].transform(
            lambda x: x.fillna(x.mean())
        )
    return df

def fill_missing_values(df):
    """Заполнение пропусков подходящими значениями."""
    df = df.copy()
    # Заполняем нулями
    df['snowfall'] = df['snowfall'].fillna(0)
    df['preciptotal'] = df['preciptotal'].fillna(0)
    df['depart'] = df['depart'].fillna(0)
    df['heat'] = df['heat'].fillna(0)
    df['cool'] = df['cool'].fillna(0)

    # Заполняем средним значением
    df['dewpoint'] = df['dewpoint'].fillna(df['dewpoint'].mean())
    df['wetbulb'] = df['wetbulb'].fillna(df['wetbulb'].mean())
    df['sealevel'] = df['sealevel'].fillna(df['sealevel'].mean())
    df['resultspeed'] = df['resultspeed'].fillna(df['resultspeed'].mean())
    df['resultdir'] = df['resultdir'].fillna(df['resultdir'].mean())
    df['sunrise'] = df['sunrise'].fillna(df['sunrise'].mean())
    df['sunset'] = df['sunset'].fillna(df['sunset'].mean())

    return df

# Удаляем неинформативные столбцы
def drop_useless_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Удалить неинформативные столбцы.
    """
    useless_cols = ['stnpressure'] # Есть sealevel
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


def preprocess(path: str) -> pd.DataFrame:
    """Вся цепочка предобработки данных."""
    df = load_data_from_file(path)
    df = convert_numeric_columns(df)
    df = convert_time_columns(df)
    df = fill_weather_nan(df)
    df = fill_missing_values(df)
    df = encode_codesum(df)
    df = drop_useless_columns(df)
    df = create_id(df)
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

def combine_sunset_sunrise(df):
    """Создание признака 'daylight_duration' (продолжительность светового дня)."""
    df = df.copy()
    df['daylight_duration'] = df['sunset'] - df['sunrise']
    df = df.drop(['sunrise', 'sunset'], axis=1)
    return df


def add_features(df):
    """Объединение всех этапов добавления признаков, кроме продаж"""
    df = add_time_features(df)
    df = add_weather_features(df)
    df = add_rolling_weather_features(df)
    df = add_holiday_feature(df)
    df = combine_sunset_sunrise(df)
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


if __name__ == '__main__':
    data = load_data()
    # create_report(data, 0)
    df = preprocess('data/merged_data.csv')
    print(df.head())
    # Сохраняем в файл
    df.to_csv('data/processed_data.csv', index=False) # 4617600
    create_report(df, 1)

    df = load_data_from_file('data/processed_data.csv')
    print(df.info())
    df = remove_units_outliers(df)
    df = add_features(df)
    print(df.info())
    df.to_csv('data/data_add_features.csv', index=False)
    df = load_data_from_file('data/data_add_features.csv')
    df = remove_zero_sales(df) # Осталось 5% от данных: 236036 вместо 4617600
    df = add_sales_features(df)
    print(df.info())
    df.to_csv('data/data_clean.csv', index=False)
    create_report(df, 2)

    # df = load_data_from_file('data/data_clean.csv')
    # print(df.info())