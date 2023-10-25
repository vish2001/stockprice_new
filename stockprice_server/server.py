import requests
import rpyc
import pandas as pd
from sklearn.linear_model import LinearRegression
from rpyc.utils.server import ThreadPoolServer

# Get an Alpha Vantage API key
api_key = "TB79OG194QZG569B"
#"2SAX71VRPODCEN74"

class StockPriceServer(rpyc.Service):
  def __init__(self):
        # Initialize an empty cache dictionary
        self.stock_cache = {}

  def on_connect(self, conn):
        pass
  def on_disconnect(self, conn):
        pass

  def exposed_get_current_price(self, symbols):
    # Implement this method to find the current price for the given symbol.
   
    prices = dict()
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="+symbol+"&interval=1min&outputsize=full&apikey="+ api_key
        response = requests.get(url)
        data = response.json()
        data = data["Time Series (1min)"]
        data = pd.DataFrame(data).transpose()
        data.columns = ["Open", "High", "Low", "Close", "Volume"]
        # Choose a prediction model
        model = LinearRegression()
        # Train the prediction model
        model.fit(data[:-1], data["Close"][1:])
        # Make a prediction
        prices.update({symbol:model.predict(data[-1:])[0]})
    
    return prices
  
if __name__ == "__main__":
    from rpyc.utils.server import ThreadPoolServer
    server = ThreadPoolServer(StockPriceServer(), port=8000)
    server.start()