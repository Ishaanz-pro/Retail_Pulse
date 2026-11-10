FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY frontend ./frontend
RUN pip install --no-cache-dir ".[dev]"
COPY .env.example .env
EXPOSE 8000
CMD ["uvicorn", "retailpulse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
