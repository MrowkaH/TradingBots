"""
Configuration settings for the AutoNewsTrade application.
"""

# API Keys (you should set these as environment variables in production)
ALPHA_VANTAGE_API_KEY = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Get one at https://www.alphavantage.co/

# Data directories
DATA_DIR = 'data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
PROCESSED_DATA_DIR = f'{DATA_DIR}/processed'

# Tickers to track (we'll start with a few major companies)
DEFAULT_TICKERS = [
    'AAPL',    # Apple
    'MSFT',    # Microsoft
    'GOOGL',   # Alphabet (Google)
    'AMZN',    # Amazon
    'META',    # Meta (Facebook)
    'TSLA',    # Tesla
    'JPM',     # JPMorgan Chase
    'JNJ',     # Johnson & Johnson
    'V',       # Visa
    'PG'       # Procter & Gamble
]

# Date ranges for historical data
HISTORIC_START_DATE = '2018-01-01'
HISTORIC_END_DATE = '2023-12-31'
