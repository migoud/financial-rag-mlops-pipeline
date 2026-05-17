CREATE OR REPLACE TABLE `project-2e0885aa-8f3e-4da5-86a.finance_ml_engine.cleaned_features` AS
SELECT 
  bls_data.year,
  bls_data.value AS us_cpi,
  wdi_data.country_name,
  wdi_data.value AS gdp_per_capita
FROM 
  `bigquery-public-data.bls.cpi_u` AS bls_data
JOIN 
  `bigquery-public-data.world_bank_wdi.indicators_data` AS wdi_data
  ON bls_data.year = wdi_data.year
WHERE 
  bls_data.series_id = 'CUUR0000SA0'
  AND wdi_data.indicator_name = 'GDP per capita (current US$)'
  AND wdi_data.country_code = 'CAN'
  AND bls_data.year >= 2010;
