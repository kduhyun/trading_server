#docker build --pull -t trading_server .
FROM python:3

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir Flask && \
    pip install --no-cache-dir pybit && \
    pip install --no-cache-dir pyyaml && \
    pip install --no-cache-dir v20

ENV FLASK_APP=/myapp/trading_server.py
ENV FLASK_ENV=production
ENV OANDA_TOKEN="your_oanda_token"
ENV BYBIT_API_KEY="your_bybit_api_key"
ENV BYBIT_API_SECRET="your_bybit_api_secret"

CMD flask run --host=0.0.0.0
