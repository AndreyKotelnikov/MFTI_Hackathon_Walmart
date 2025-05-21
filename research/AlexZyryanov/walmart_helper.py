import pandas as pd
import numpy as np

def fill_weekly_station_year(df, col):
    filled = df.copy()
    means = (
        df.groupby(['station_nbr', 'year', 'week'])[col]
        .mean()
        .rename('week_mean')
        .reset_index()
    )
    filled = filled.merge(means, on=['station_nbr', 'year', 'week'], how='left')
    filled[col] = filled[col].fillna(filled['week_mean'])
    filled.drop(columns='week_mean', inplace=True)
    return filled

def fill_weekly_station(df, col):
    filled = df.copy()
    means = (
        df.groupby(['station_nbr', 'week'])[col]
        .mean()
        .rename('week_mean')
        .reset_index()
    )
    filled = filled.merge(means, on=['station_nbr', 'week'], how='left')
    filled[col] = filled[col].fillna(filled['week_mean'])
    filled.drop(columns='week_mean', inplace=True)
    return filled

def fill_week_global(df, col):
    filled = df.copy()
    means = (
        df.groupby(['week'])[col]
        .mean()
        .rename('week_mean')
        .reset_index()
    )
    filled = filled.merge(means, on='week', how='left')
    filled[col] = filled[col].fillna(filled['week_mean'])
    filled.drop(columns='week_mean', inplace=True)
    return filled
