#docker build --pull -t trading_server .
FROM python:3

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir Flask && \
    pip install --no-cache-dir pybit && \
    pip install --no-cache-dir pyyaml && \
    pip install --no-cache-dir v20

ENV FLASK_APP=/myapp/trading_server.py
ENV FLASK_ENV=production
ENV OANDA_TOKENS="your_oanda_tokens separated by comma(,)"
ENV BYBIT_API_KEYS="your_bybit_api_keys separated by comma(,)"
ENV BYBIT_API_SECRETS="your_bybit_api_secrets separated by comma(,)"

CMD flask run --host=0.0.0.0
