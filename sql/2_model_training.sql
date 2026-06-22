CREATE OR REPLACE MODEL `project-2e0885aa-8f3e-4da5-86a.finance_ml_engine.gdp_prediction_model`
OPTIONS(
  model_type='linear_reg',
  input_label_cols=['gdp_per_capita_local_currency'],
  optimize_strategy='batch_gradient_descent',
  l1_reg=0.1,
  l2_reg=0.1
) AS
SELECT 
  us_cpi,
  gdp_per_capita_local_currency
FROM 
  `project-2e0885aa-8f3e-4da5-86a.finance_ml_engine.cleaned_features`;
WHERE
  country_code = 'CAN' ;
