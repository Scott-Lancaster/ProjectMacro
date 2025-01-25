import requests
from bs4 import BeautifulSoup

def get_bitcoin_price():
    # Define the Yahoo Finance URL for Bitcoin
    url = 'https://finance.yahoo.com/quote/BTC-USD'

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the element containing the Bitcoin price
        price_element = soup.find('td', {'data-test': 'OPEN-value'})

        # Extract the text from the price element
        bitcoin_price = price_element.text.strip()

        return bitcoin_price
    else:
        print('Failed to retrieve data. Status code:', response.status_code)
        return None

if __name__ == "__main__":
    bitcoin_price = get_bitcoin_price()
    if bitcoin_price:
        print(f'Bitcoin Price: {bitcoin_price}')
    else:
        print('Unable to fetch Bitcoin price.')
