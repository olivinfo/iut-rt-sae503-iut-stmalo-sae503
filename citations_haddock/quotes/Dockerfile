FROM python:3.12-slim
LABEL org.opencontainers.image.source=https://github.com/olivinfo/sae503-kc-md
WORKDIR /app

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y curl --no-install-recommends

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser user
USER user

COPY quotes/ .
COPY data/ .

ENV REDIS_HOST="backend-redis"

EXPOSE 5000

# HEALTHCHECK --interval=1m --timeout=30s --retries=3 CMD curl --fail http://localhost:5000 || exit 1
HEALTHCHECK --interval=5s --timeout=2s --retries=2 --start-period=5s CMD curl --fail http://localhost:5000/quotes/health || exit 1

CMD ["python", "quotes.py"]

