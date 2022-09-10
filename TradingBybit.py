from pybit import HTTP  # supports inverse perp & futures, usdt perp, spot.

class TradingBybit:

    def __init__(self, bybitApiKey, bybitApiSecret):

        self.session_auth = HTTP(
            endpoint="https://api.bybit.com",
            api_key=bybitApiKey,
            api_secret=bybitApiSecret
        )

    def orderForBybit(self, code, position, price, positionSize, action):

        code = code.upper()

        usdt=self.session_auth.get_wallet_balance(coin = "USDT")['result']['USDT']['equity']
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
            result = self.session_auth.place_active_order_bulk(orders)
            return result[0]['result']['order_id']

        return "-1"
