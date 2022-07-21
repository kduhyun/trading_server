from pybit import HTTP  # supports inverse perp & futures, usdt perp, spot.
from flask import Flask, request, jsonify
import v20
import yaml
import logging
import os


##windows: set FLASK_APP=trading_server.py
##linux: export FLASK_APP=trading_server.py
##flask run

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

myOandaToken = os.getenv("OANDA_TOKEN", "")
bybitApiKey = os.getenv("BYBIT_API_KEY", "")
bybitApiSecret = os.getenv("BYBIT_API_SECRET", "")

oandaAPI = v20.Context(
    "api-fxtrade.oanda.com",
    443,
    True,
    application="dudu_bot",
    token=myOandaToken,
    datetime_format="RFC3339"
)

response = oandaAPI.account.list()
oandaAccounts = [account.id for account in response.body.get("accounts")]

oandaMainAccountId = oandaAccounts[0]

def getMyBalance(accountId):
    response = oandaAPI.account.summary(accountId)

    accountInfo = response.body.get("account")
    myBalance = accountInfo.marginCloseoutNAV
    return myBalance


session_auth = HTTP(
    endpoint="https://api.bybit.com",
    api_key=bybitApiKey,
    api_secret=bybitApiSecret
)

@app.route('/')
def index():
  return 'Server Works!'

@app.route('/oanda/order/<code>/<position>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForOandaWithPosition(code, position, price, positionSize):

    content = request.json
    action = content['action']
    return orderForOanda(code.upper(), position, price, positionSize, action)

@app.route('/oanda/order/<code>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForOandaWithoutPosition(code, price, positionSize):

    content = request.json
    action = content['action']
    position = content['position']
    return orderForOanda(code.upper(), position, price, positionSize, action)


def orderForOanda(code, position, price, positionSize, action):

    myBalance=getMyBalance(oandaMainAccountId)

    marginRequired=myBalance*100
    instrument = "US100_USD"

    code = code.upper()
    roundFigure = 1
    if code == "NQ":
        marginRequired = 2200
        instrument = "NAS100_USD"
    elif code == "ES":
        marginRequired = 560
        instrument = "SPX500_USD"
    elif code == "RTY":
        marginRequired = 280
        instrument = "US2000_USD"
    elif code == "DE":
        marginRequired = 3040
        instrument = "DE30_EUR"
    elif code == "HG":
        roundFigure = 0
        marginRequired = 0.39
        instrument = "XCU_USD"
    elif code == "PL":
        marginRequired = 252
        instrument = "XPT_USD"
    elif code == "CL":
        roundFigure = 0
        marginRequired = 17
        instrument = "WTICO_USD"
    elif code == "SI":
        marginRequired = 6
        roundFigure = 0
        instrument = "XAG_USD"


    quantity = round((myBalance/marginRequired)*positionSize, roundFigure)

    if quantity < 0.1:
        quantity = 0.1

    if position == "short":
        quantity = -quantity

    output="error"

    if action == "open":
        order = {
            "type":"MARKET",
            "instrument":instrument,
            "units": str(quantity),
            "timeInForce":"FOK",
            "positionFill":"DEFAULT"
        }
        response=oandaAPI.order.market( oandaMainAccountId, **order )
        app.logger.info(response.body)
        output = response.get("lastTransactionID")
    elif action == "close":
        order = {}
        if position == "long":
            order = {
                "instrument":instrument,
                "longUnits": "ALL"
            }
        elif position == "short":
            order = {
                "instrument":instrument,
                "shortUnits": "ALL"
            }

        response = oandaAPI.position.close(oandaMainAccountId, **order)
        app.logger.info(response.body)
        output = response.get("lastTransactionID")

    return output



@app.route('/bybit/order/<code>/<position>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForBybitWithPosition(code, position, price, positionSize):
    content = request.json
    action = content['action']

    if price < 0.001:
        price = float(content["price"])

    return orderForBybit(code.upper(), position, price, positionSize, action)

@app.route('/bybit/order/<code>/<float:price>/with/<float:positionSize>', methods = ['GET','POST'])
def orderForBybitWithoutPosition(code, price, positionSize):

    content = request.json
    action = content['action']
    position = content['position']

    if price < 0.001:
        price = float(content["price"])

    return orderForBybit(code.upper(), position, price, positionSize, action)


def orderForBybit(code, position, price, positionSize, action):

    code = code.upper()

    usdt=session_auth.get_wallet_balance(coin = "USDT")['result']['USDT']['equity']
    quantity = round((usdt/price) * positionSize, 4)

    orders = []
    if action=="open":
        side = ""
        take_profit = 0.0
        stop_loss = 0.0
        if position=="long":
            side="Buy"
            take_profit=round(float(price)*1.05,2)
            stop_loss=round(float(price)*0.96,2)
        elif position=="short":
            side="Sell"
            take_profit=round(float(price)*0.96,2)
            stop_loss=round(float(price)*1.05,2)

        orders = [{
            "symbol": code,
            "order_type": "Limit",
            "side": side,
            "qty": quantity,
            "price": round(float(price),2),
            "time_in_force": "GoodTillCancel",
            "reduce_only":False,
            "close_on_trigger":False,
            "take_profit": take_profit,
            "stop_loss":stop_loss
        }]
    elif action=="close":
        side = ""
        if position=="long":
            side="Sell"

        elif position=="short":
            side="Buy"

        orders = [{
            "symbol": code,
            "order_type": "Market",
            "side": side,
            "qty": round(quantity*100, 2),
            "time_in_force": "GoodTillCancel",
            "reduce_only":True,
            "close_on_trigger":False
        }]

    if len(orders) > 0:
        result = session_auth.place_active_order_bulk(orders)
        return result[0]['result']['order_id']

    return "-1"
