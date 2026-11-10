CREATE TABLE IF NOT EXISTS sales_fact (
  transaction_id STRING NOT NULL,
  order_id STRING NOT NULL,
  product_id STRING NOT NULL,
  warehouse_id STRING NOT NULL,
  quantity INT64 NOT NULL,
  unit_price NUMERIC NOT NULL,
  revenue NUMERIC NOT NULL,
  transaction_ts TIMESTAMP NOT NULL
);
