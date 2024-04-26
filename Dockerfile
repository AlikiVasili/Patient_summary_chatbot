# Use an official Python runtime as a parent image
FROM python:3.12.3-slim
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /var/lib/apt/lists/*

COPY . /app

EXPOSE 5000
ENV FLASK_APP=chatbot_app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
