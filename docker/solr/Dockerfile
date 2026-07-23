FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY load_data.py .
COPY data ./data

CMD ["python", "load_data.py"]
