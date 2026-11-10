# Deployment

Local development is the supported zero-cost path. For GCP, set `GCP_PROJECT_ID` and
authenticate with Application Default Credentials. Enable Cloud Storage, BigQuery,
Pub/Sub, Dataflow, Cloud SQL Admin, Cloud Run, Cloud Build, Logging, and Monitoring APIs.

The cloud optional dependency is installed with `pip install -e '.[cloud]'`. The same
validated batch tables can be loaded to BigQuery; Pub/Sub publishers and Beam runners
should be enabled only after reviewing IAM and cost. Use a dedicated service account with
least privilege (`storage.objectAdmin` on the bucket, `bigquery.dataEditor` on the
dataset, `pubsub.publisher` on the topic, and Dataflow worker permissions for Dataflow).

Do not commit service-account JSON files. Cloud Run should receive secrets through Secret
Manager, not plain environment files. Cloud SQL requires private networking and backups.
Delete test resources explicitly with the corresponding `gcloud`/Terraform destroy command.
