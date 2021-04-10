# Bitmex_Wrapper
This is a Bitmex Wrapper: You can create an object of the class "bitmex_wrapper" which will then subscribe connect to the Bitmex Websocket and Subscribe to all of your datafeed you parse and check whether everything went well. By default I only programmed to handle the orderbook_L25 datafeed of Bitmex which is stored in self.bid_list and self.ask_list and I store the best bid and best ask price as well as size seperate in self.best_bid/ask_price and self.best_bid/ask_size. Have to to play around with it :)

Need following modules to be imported:
import websocket
import json
import numpy
