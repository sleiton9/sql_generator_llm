FROM python:3.10.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p data/raw data/stage data/analytics logs

EXPOSE 8000

CMD ["python", "-m", "src"]
