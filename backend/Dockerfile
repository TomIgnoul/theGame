FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Copy only dependency files first (better caching)
COPY pyproject.toml /app/

# Install deps (no venv inside container)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy app
COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

