# Architecture

RetailPulse separates ingestion, governance, processing, storage, ML, API, and UI
boundaries. Local processing is deterministic and uses SQLite/Parquet-compatible files.
The cloud path maps raw files to Cloud Storage, analytical facts to BigQuery, events to
Pub/Sub and Beam/Dataflow, transactional state to Cloud SQL, and the API/UI to Cloud Run.
The same schemas and validation rules are intended to be reused in both modes.
