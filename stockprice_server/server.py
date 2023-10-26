import rpyc
import requests
import logging
from rpyc.utils.server import ThreadPoolServer
from datetime import datetime
import sys

# Configure the logging settings
logging.basicConfig(level=logging.INFO)

# Marketstack API key
api_key = '7075fc97a8e59c82b055171cd5037ed3'

class StockDataFetcher:
    def __init__(self):
        # Initialize an empty cache dictionary
        self.stock_cache = {}

    def store_data_in_cache(self, symbol, data):
        # Store the data in the cache dictionary along with the current date
        current_date = data['date']
        self.stock_cache[symbol] = {'data': data, 'date': current_date}
        logging.debug(f"Data for symbol '{symbol}' stored in cache with date {current_date}.")

    def get_data_from_cache(self, symbol):
        # Retrieve data from the cache dictionary
        cache_entry = self.stock_cache.get(symbol)
        if cache_entry is not None:
            # Check if the cache entry is more than one day old
            current_date_obj = cache_entry['date']
            datetime_obj = datetime.strptime(current_date_obj, "%Y-%m-%dT%H:%M:%S%z")
            curr_date = datetime_obj.date()
            if curr_date != datetime.now().date():
                # Invalidate the cache entry if it's older than one day
                logging.debug(f"Cache entry for symbol '{symbol}' is older than one day. Invalidating.")
                del self.stock_cache[symbol]
                return None
            else:
                logging.debug(f"Data for symbol '{symbol}' found in cache.")
                return cache_entry['data']
        else:
            logging.debug(f"Data for symbol '{symbol}' not found in cache.")
            return None

    def fetch_latest_stock_data(self, symbol: str):
        url = "http://api.marketstack.com/v1/eod"
        params = {
            "access_key": api_key,
            "symbols": symbol
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                latest_data = data['data'][0]
                # Get the latest data entry
                return {
                    'close': latest_data['close'],
                    'date': latest_data['date']
                }
            else:
                logging.debug(f"Request failed with status code {response.status_code}")
        except Exception as e:
            logging.debug(f"An error occurred: {str(e)}")


class StockService(rpyc.Service):
    def __init__(self):
        self.stock_data_fetcher = StockDataFetcher()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_fetch_stock_data(self, req_params):
        client_id = req_params["client_id"]
        symbols = req_params['symbols']

        def fetch_symbol_price(symbol):
            # First search the cache if data already exists
            fetched_symbol_data = self.stock_data_fetcher.get_data_from_cache(symbol)

            # If there is no available data in the cache, fetch new data
            if fetched_symbol_data is None:
                fetched_symbol_data = self.stock_data_fetcher.fetch_latest_stock_data(symbol)
                # Store the newly fetched data in the local cache
                if fetched_symbol_data is not None:
                    self.stock_data_fetcher.store_data_in_cache(symbol, fetched_symbol_data)
                    logging.debug(f'Data for {symbol} fetched from API and stored in cache.')
            data = fetched_symbol_data
            return {'symbol': symbol, 'data': data}

        # Use a list comprehension to fetch data for all symbols
        reply = [fetch_symbol_price(symbol) for symbol in symbols]

        #logging.info(f'Client {client_id} requested data for {symbols}: Server replied {reply}')
        return reply


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    portn = int(sys.argv[1])
    server = ThreadPoolServer(StockService(), port=portn)
    logging.info("Starting Stock Data RPC Server...")
    server.start()
