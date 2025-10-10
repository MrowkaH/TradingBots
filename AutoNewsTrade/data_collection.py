""
Data collection module for AutoNewsTrade.
Handles downloading and storing financial data from various sources.
"""
import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import logging

from config import (
    ALPHA_VANTAGE_API_KEY, 
    RAW_DATA_DIR, 
    PROCESSED_DATA_DIR,
    DEFAULT_TICKERS,
    HISTORIC_START_DATE,
    HISTORIC_END_DATE
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autonewstrade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create directories if they don't exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

class DataCollector:
    """Class for collecting financial data from various sources."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ALPHA_VANTAGE_API_KEY
        self.yf = yf.Tickers(" ".join(DEFAULT_TICKERS))
        
    def get_historical_prices(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get historical price data for a given ticker."""
        start_date = start_date or HISTORIC_START_DATE
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        
        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                show_errors=False
            )
            
            if data.empty:
                logger.warning(f"No price data found for {ticker}")
                return pd.DataFrame()
                
            # Save raw data
            data.to_csv(f"{RAW_DATA_DIR}/{ticker}_prices.csv")
            logger.info(f"Successfully downloaded price data for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error downloading price data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_earnings_calendar(self, ticker: str) -> pd.DataFrame:
        """Get upcoming earnings dates for a given ticker."""
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            
            if calendar is None or calendar.empty:
                logger.warning(f"No earnings calendar data found for {ticker}")
                return pd.DataFrame()
                
            # Save raw data
            calendar.to_csv(f"{RAW_DATA_DIR}/{ticker}_earnings_calendar.csv")
            logger.info(f"Successfully downloaded earnings calendar for {ticker}")
            return calendar
            
        except Exception as e:
            logger.error(f"Error downloading earnings calendar for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_historical_earnings(self, ticker: str) -> pd.DataFrame:
        """Get historical earnings data for a given ticker."""
        try:
            stock = yf.Ticker(ticker)
            earnings = stock.earnings
            
            if earnings is None or earnings.empty:
                logger.warning(f"No historical earnings data found for {ticker}")
                return pd.DataFrame()
                
            # Save raw data
            earnings.to_csv(f"{RAW_DATA_DIR}/{ticker}_historical_earnings.csv")
            logger.info(f"Successfully downloaded historical earnings for {ticker}")
            return earnings
            
        except Exception as e:
            logger.error(f"Error downloading historical earnings for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def collect_all_data(self, tickers: List[str] = None) -> None:
        """Collect all available data for the given tickers."""
        tickers = tickers or DEFAULT_TICKERS
        
        for ticker in tickers:
            logger.info(f"Collecting data for {ticker}...")
            
            # Get price data
            self.get_historical_prices(ticker)
            
            # Get earnings data
            self.get_earnings_calendar(ticker)
            self.get_historical_earnings(ticker)
            
            # Be nice to the API
            time.sleep(1)

def main():
    """Main function to run data collection."""
    logger.info("Starting data collection...")
    
    collector = DataCollector()
    
    # Collect data for all default tickers
    collector.collect_all_data()
    
    logger.info("Data collection complete!")

if __name__ == "__main__":
    main()
