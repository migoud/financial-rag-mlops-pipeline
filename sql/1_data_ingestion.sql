CREATE OR REPLACE TABLE `project-2e0885aa-8f3e-4da5-86a.finance_ml_engine.cleaned_features` AS
WITH annual_us_cpi AS (
  SELECT 
    year,
    AVG(value) AS avg_us_cpi
  FROM 
    `bigquery-public-data.bls.cpi_u`
  WHERE 
    series_id = 'CUUR0000SA0'
    AND year >= 2010
  GROUP BY 
    year
)
SELECT 
  cpi.year,
  ROUND(cpi.avg_us_cpi, 2) AS us_cpi,
  wdi_data.country_code,
  wdi_data.country_name,
  -- This will be in CAD for Canada, and USD for the United States
  ROUND(wdi_data.value, 2) AS gdp_per_capita_local_currency 
FROM 
  annual_us_cpi AS cpi
JOIN 
  `bigquery-public-data.world_bank_wdi.indicators_data` AS wdi_data
  ON cpi.year = wdi_data.year
WHERE 
  wdi_data.indicator_name = 'GDP per capita (current LCU)' -- Local Currency Unit (CAD / USD)
  AND wdi_data.country_code IN ('CAN', 'USA'); -- Filtered strictly to Canada and the United States
