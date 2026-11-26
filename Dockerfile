FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-beng ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py voice_engine.py avatar_engine.py index.html ./
ENV CLOUD_LITE=1 HOST=0.0.0.0 PORT=10000
EXPOSE 10000
CMD ["python","-u","server.py"]
