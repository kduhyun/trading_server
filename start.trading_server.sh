docker stop trading
docker rm trading
docker run --name trading -d -v "$PWD":/myapp -p 5000:5000 -w /myapp trading_server
