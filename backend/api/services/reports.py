from hackathon.sources_db import runQuery


def churn_sales_report(sign='>='):
    return runQuery(f'''
SELECT
    TO_CHAR(period, 'MM.YYYY') AS timeline_month,
    COUNT(DISTINCT customer_unique_id) AS customer_count
FROM (
    -- Исторические данные
    SELECT 
        customer_unique_id, 
        timeline_date AS period, 
        pred_proba
    FROM customer_features_timeline
    
    UNION ALL
    
    -- Текущие данные (с приведением к той же структуре)
    SELECT 
        customer_unique_id, 
        timeline_date::date AS period,
        pred_proba
    FROM customer_features_current

) AS unified_data
WHERE pred_proba {sign} 0.5
GROUP BY TO_CHAR(period, 'MM.YYYY')
ORDER BY MIN(period);''')