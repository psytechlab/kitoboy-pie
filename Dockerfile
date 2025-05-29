FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir data && \
    python -c "import urllib.request; \
    urllib.request.urlretrieve('https://storage.yandexcloud.net/natasha-navec/packs/navec_news_v1_1B_250K_300d_100q.tar', 'data/navec_news_v1_1B_250K_300d_100q.tar'); \
    urllib.request.urlretrieve('https://storage.yandexcloud.net/natasha-slovnet/packs/slovnet_ner_news_v1.tar', 'data/slovnet_ner_news_v1.tar')"
COPY . .
EXPOSE 5900
CMD ["fastapi", "run", "app/main.py", "--port", "5900"]