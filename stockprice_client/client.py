import rpyc
import time
import logging
import random

class StockPriceClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.total_response_time = 0
        self.num_responses = 0
        self.conn = None
    def connect(self):
        # Create a connection to the remote service using the provided 'host' and 'port'.
        try:
        # Create a connection to the remote service using the provided 'host' and 'port'.
            self.conn = rpyc.connect(self.host, self.port)
        except Exception as e:
            logging.error(f"Error connecting to the server: {str(e)}")
            self.conn = None
    def is_connected(self):
        # Check if the connection is established and the connection object is not None
        return self.conn is not None
    def disconnect(self):
        # Close the connection if it's open
        if self.is_connected():
            self.conn.close()
            self.conn = None

    def fetch_stock_prices(self, symbols):
        if not self.is_connected():
            self.connect()
        try:
            # Time before the RPC call
            start_time = time.perf_counter_ns()
            current_prices = self.conn.root.exposed_fetch_stock_data(symbols)
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
        except EOFError:
            # Handle EOFError when the stream has been closed
            logging.error('Stream has been closed. Reconnecting...')
            self.connect()
            return None
        except Exception as e:
            logging.error(f'Error fetching stock price data: {str(e)}')
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = StockPriceClient("nginx", 8087)
    # List of symbols to fetch prices for.
    symbols = [
    "AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "NVDA",  
    "NFLX", "DIS", "FB", "TWTR", "AMD", "INTC",      
    "IBM", "ORCL", "CSCO", "HPQ", "QCOM", "SAP",     
    "V", "MA", "PYPL", "SQ", "PYPL",                  
    "JPM", "GS", "BAC", "WFC", "C"                    
    ]
    
    symbols_mapped = random.sample(symbols, random.randint(1, 6))
    logging.info("sent symbols:")
    logging.info(symbols_mapped)
    prices = client.fetch_stock_prices(symbols_mapped)
    logging.debug(prices)
    try:    
        if prices is not None:
            for item in prices:
                symbol = item['symbol']
                if item['data'] is not None :
                    price = item['data']['close']
                    print(f"Symbol: {symbol} and Price: ${price}")
                    #client.disconnect()
                else:
                    continue
        else:
            print("Error fetching stock prices.")
    except EOFError:
        # Handle EOFError specifically, such as reconnecting or terminating gracefully
        logging.error("EOF error")
        client.connect()  # Reconnect or take appropriate actions
    except Exception as e:
        # Handle other exceptions as needed
        logging.error(f"Error: {e}")   
    # Sleep for a random amount of time between 0.5 seconds and 1 seconds
    sleep_time = random.uniform(0.5, 1)
    time.sleep(sleep_time)