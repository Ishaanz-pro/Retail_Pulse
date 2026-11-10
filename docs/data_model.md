# Data model

The local analytical model contains `products_dim`, `warehouses_dim`, and `sales_fact`.
The cloud design extends this with customers, orders, order_items, inventory,
delivery_events, product_forecasts, anomaly_events, and pipeline_runs. Facts use stable
synthetic IDs, UTC timestamps, positive-value checks, and foreign keys to dimensions.
BigQuery partitioning should use event date; clustering should use product and warehouse.
