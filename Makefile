install:
	pip install -e ".[dev]"
data:
	python -m retailpulse.ingestion.generate --records 50000
batch:
	python -m retailpulse.processing.batch
test:
	pytest
lint:
	ruff check src tests frontend
