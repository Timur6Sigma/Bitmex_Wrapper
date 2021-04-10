import websocket
import json
import numpy

class bitmex_wrapper:
    def __init__(self, numpy, json, websocket, subscriptions):

        # Establish connection with the Bitmex-websocket
        # and subscribe to the parsed datafeed and instrument

        self.initiation_okay = "Initiation Okay :-)"    # initVarFirstTime
        self.numpy = numpy  # initVarFirstTime
        self.json = json    # initVarFirstTime
        self.ws = websocket # initVarFirstTime
        self.subscriptions = subscriptions  # initVarFirstTime

        self.bid_list = None    # initVarFirstTime
        self.ask_list = None    # initVarFirstTime
        self.best_bid_price = None  # initVarFirstTime
        self.best_ask_price = None  # initVarFirstTime
        self.best_bid_size = None   # initVarFirstTime
        self.best_ask_size = None   # initVarFirstTime
        self.symbol, self.id, self.side, self.size, self.price = 0, 1, 2, 3, 4  # initVarFirstTime

        try:
            self.ws = self.ws.create_connection("wss://www.bitmex.com/realtime")
            response = self.json.loads(self.ws.recv())
            print(response)
            should_be_welcome_text = "Welcome to the BitMEX Realtime API."

            try:
                if not (response["info"] == should_be_welcome_text):
                    self.initiation_okay = "Failed at welcome text(1)"
            except:
                self.initiation_okay = "Failed at welcome text(2)"
        except:
            self.initiation_okay = "Failed to establish connection(1)"

        if self.initiation_okay == "Initiation Okay :-)":
            try:
                for i in range(len(self.subscriptions)):
                    self.ws.send(self.json.dumps({"op": self.subscriptions[i]["op"], "args": [self.subscriptions[i]["arg1"] + ":" + self.subscriptions[i]["arg2"]]}))
                    response = json.loads(self.ws.recv())
                    print(response)
                    try:
                        if not (response["success"] and response["subscribe"] == self.subscriptions[i]["arg1"] + ":" + self.subscriptions[i]["arg2"]):
                            self.initiation_okay = "Failed to verify subscribtion(1)"
                    except:
                        self.initiation_okay = "Failed to verify subscribtion(2)"
            except:
                self.initiation_okay = "Failed to subscribe(1)"


    def receive_and_distribute_responses_to_handlers(self):
        response = self.json.loads(self.ws.recv())
        if response["table"] == "orderBookL2_25":
            self.handle_orderBookL2_25_response(response)
            if self.bid_list is not None and self.ask_list is not None:
                if self.bid_list.size and self.ask_list.size:
                    self.get_best_quotes()


    def handle_orderBookL2_25_response(self, response):
        if response["action"] == "update":
            for row in response["data"]:
                rowDictKeys = list(row.keys())
                if row["side"] == "Buy":
                    index = self.numpy.where(self.bid_list[:, self.id] == str(row["id"]))
                    if "size" in rowDictKeys:
                        self.bid_list[index, self.size] = row["size"]
                elif row["side"] == "Sell":
                    index = self.numpy.where(self.ask_list[:, self.id] == str(row["id"]))
                    if "size" in rowDictKeys:
                        self.ask_list[index, self.size] = row["size"]

        elif response["action"] == "delete":
            for row in response["data"]:
                if row["side"] == "Buy":
                    index = self.numpy.where(self.bid_list[:, self.id] == str(row["id"]))
                    self.bid_list = self.numpy.delete(self.bid_list, index, axis=0)
                else:
                    index = self.numpy.where(self.ask_list[:, self.id] == str(row["id"]))
                    self.ask_list = self.numpy.delete(self.ask_list, index, axis=0)

        elif response["action"] == "insert":
            for row in response["data"]:
                if row["side"] == "Buy":
                    self.bid_list = self.numpy.vstack(
                        (self.bid_list, self.numpy.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))
                else:
                    self.ask_list = self.numpy.vstack(
                        (self.ask_list, self.numpy.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))

        elif response["action"] == "partial":
            self.bid_list = self.numpy.array([])
            self.ask_list = self.numpy.array([])

            for row in response["data"]:
                if row["side"] == "Buy":
                    if len(self.numpy.shape(self.bid_list)) == 1 and self.numpy.shape(self.bid_list)[0] == 0:
                        self.bid_list = self.numpy.append(self.bid_list, self.numpy.array(
                            [[row["symbol"], row["id"], row["side"], row["size"], row["price"]]]))
                    else:
                        self.bid_list = self.numpy.vstack(
                            (
                            self.bid_list, self.numpy.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))

                else:
                    if len(self.numpy.shape(self.ask_list)) == 1 and self.numpy.shape(self.ask_list)[0] == 0:
                        self.ask_list = self.numpy.append(self.ask_list,
                                               self.numpy.array(
                                                   [row["symbol"], row["id"], row["side"], row["size"], row["price"]]))
                    else:
                        self.ask_list = self.numpy.vstack(
                            (
                            self.ask_list, self.numpy.array([[row["symbol"], row["id"], row["side"], row["size"], row["price"]]])))

        # Max self.bid_list is in self.bid_list[0], and Min self.ask_list in self.ask_list[0]
        self.bid_list = self.bid_list[self.numpy.argsort(self.bid_list[:, self.price])[::-1]]
        self.ask_list = self.ask_list[self.numpy.argsort(self.ask_list[:, self.price])]


    def get_best_quotes(self):
        self.best_bid_price = float(self.bid_list[0][self.price])
        self.best_ask_price = float(self.ask_list[0][self.price])
        self.best_bid_size = int(self.bid_list[0][self.size])
        self.best_ask_size = int(self.ask_list[0][self.size])

if __name__ == '__main__':

    subscriptions = [{"op": "subscribe", "arg1": "orderBookL2_25", "arg2": "XBTUSD"}]

    bitmex_wrapper = bitmex_wrapper(numpy, json, websocket, subscriptions)

    print(bitmex_wrapper.initiation_okay)

    for i in range(1500):
        bitmex_wrapper.receive_and_distribute_responses_to_handlers()
        print(bitmex_wrapper.best_bid_price, bitmex_wrapper.best_ask_price)

