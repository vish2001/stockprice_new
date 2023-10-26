import rpyc
import time
import logging
import random

class StockPriceClient:
    def __init__(self, host, port):
        self.conn = rpyc.connect(host, port)
        self.total_response_time = 0
        self.num_responses = 0

    def fetch_stock_prices(self, symbols):
        try:
            # Time before the RPC call
            start_time = time.perf_counter_ns()
            current_prices = self.conn.root.exposed_fetch_stock_data({"client_id": "client1", "symbols": symbols})
            # After receiving the response
            end_time = time.perf_counter_ns()
            response_time = end_time - start_time
            # Update the total response time and number of responses
            self.total_response_time += response_time
            self.num_responses += 1
            # Calculate the mean response time
            mean_response_time = self.total_response_time / self.num_responses
            logging.info(f"Mean response time: {mean_response_time / 1000000} ms")
            return current_prices
        except Exception as e:
            logging.error(f'Error fetching stock data: {str(e)}')
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = StockPriceClient("nginx", 8087)
    # List of symbols to fetch prices for
    symbols = ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "NVDA"]
    prices = client.fetch_stock_prices(symbols)

    if prices:
        for item in prices:
            symbol = item['symbol']
            price = item['data']['close']
            print(f"Symbol: {symbol} and Price: ${price}")
    else:
        print("Error fetching stock prices.")
    
    # Sleep for a random amount of time between 0.5 seconds and 1 seconds
    sleep_time = random.uniform(0.5, 1)
    time.sleep(sleep_time)