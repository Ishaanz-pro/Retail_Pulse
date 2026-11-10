# Security

The local demo uses synthetic identifiers and has no authentication requirement. The
API does not expose database credentials or arbitrary SQL. Agent requests route through
allowlisted Python tools and return source table references. In a production deployment,
put Cloud Run behind identity-aware access, use Secret Manager for Gemini credentials,
apply dataset-level IAM, validate request size/rate limits, and emit audit logs for every
agent tool invocation. Never commit `.env`, credentials, or service-account keys.
