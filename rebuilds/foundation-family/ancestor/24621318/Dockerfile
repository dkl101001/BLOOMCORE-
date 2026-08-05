FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e ".[dev]"

CMD ["python", "-m", "bloomforce_core", "run", "--steps", "10", "--summary"]
