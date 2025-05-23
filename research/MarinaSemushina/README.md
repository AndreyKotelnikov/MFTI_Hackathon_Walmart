# Гипотеза:

Погодные условия и временные признаки (день недели, месяц, скользящее среднее продаж) влияют на объем продаж. 

# План работ:
1. Загрузить и предобработать данные: заполнить пропуски, создать новые признаки на основе даты и погоды, а также признаки, отражающие поведение продаж (скользящее среднее, признаки нулевых продаж).
2. Создать обучающую выборку с набором признаков.
3. Обучить и оценить несколько моделей (XGBoost, Random Forest, Линейную регрессию) с подбором гиперпараметров через GridSearchCV.
4. Провести оценку моделей по метрике RMSE на отложенной тестовой выборке.
5. Проанализировать важность признаков с помощью встроенных методов и SHAP.

# Цель:

Построить модель, которая максимально точно прогнозирует логарифм продаж (log1p), учитывая погодные и временные факторы.

# Выбор моделей:

XGBoost: хорошо работает с табличными данными, способен выявлять сложные нелинейные зависимости. Подбирались параметры n_estimators, max_depth и learning_rate.

Random Forest: устойчив к переобучению и прост в настройке, хорошо справляется с разными типами признаков. Подбирались количество деревьев и глубина.

Линейная регрессия: простая и интерпретируемая модель, служит базовым ориентиром для оценки качества более сложных моделей.

# Полученные промежуточные результаты:

Модели обучались на 80% данных, тестировались на 20%. Заполнение пропусков выполнялось средним значением.

# Метрики RMSE на тесте:

XGBoost RMSE: 0.3355

Random Forest RMSE: 0.3061

Линейная регрессия RMSE: 0.8901

Random Forest показывает наименьшее значение RMSE, что указывает на его наилучшее качество прогнозирования среди представленных моделей. 

Возможно, для более лучшей производительности стоит попробовать различные настройки для XGBoost и Random Forest, также провести кросс-валидацию.








