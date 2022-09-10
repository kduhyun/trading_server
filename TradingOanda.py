import v20

class TradingOanda:

    def __init__(self, oandaToken):
        
        self.oandaAPI = v20.Context(
            "api-fxtrade.oanda.com",
            443,
            True,
            application="dudu_bot",
            token=oandaToken,
            datetime_format="RFC3339"
        )

        response = self.oandaAPI.account.list()
        oandaAccounts = [account.id for account in response.body.get("accounts")]

        self.oandaMainAccountId = oandaAccounts[0]

    def getMyBalance(self):
        response = self.oandaAPI.account.summary(self.oandaMainAccountId)

        accountInfo = response.body.get("account")
        myBalance = accountInfo.marginCloseoutNAV
        return myBalance


    def order(self, code, position, price, positionSize, action):

        myBalance= self.getMyBalance()

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
            response=self.oandaAPI.order.market( self.oandaMainAccountId, **order )
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

            response = self.oandaAPI.position.close(self.oandaMainAccountId, **order)
            app.logger.info(response.body)
            output = response.get("lastTransactionID")

        return output
