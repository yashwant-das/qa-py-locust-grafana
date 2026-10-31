FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY app.py .

EXPOSE 5000

# One process keeps the Prometheus metrics in a single registry, and the small
# thread pool is what saturates during the spike scenario. Keep-alive outlasts
# the 1-3 second pause between a Locust user's requests, so idle connections
# are not closed just as the client reuses them.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--keep-alive", "5", "app:app"]
