# trading API server
trading API server for ```OANDA``` and ```Bybit``` written in Python3.

# prerequisite
- Docker installed server
  - to check the docker, type the command ```docker info``` and if it returns docker information, your server is ready.
- prepare ```OANDA``` api token and ```Bybit``` api key and secret.

# How to use?
1. download this repository

1. edit ```Dockerfile``` with your api token and key info.

1. run the ```build.trading_server.sh```

1. run the ```start.trading_server.sh```

1. check logs using ```tail.trading_server.sh```
