FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY users/ ./users/
COPY data/ ./data/

EXPOSE 5000

CMD ["python", "users/users.py"]
