"""
Data processing module for AutoNewsTrade.
Handles cleaning, transforming, and analyzing the collected financial data.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DEFAULT_TICKERS
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Class for processing and analyzing financial data."""
    
    def __init__(self):
        self.processed_data = {}
    
    def load_raw_data(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """Load all raw data for a given ticker."""
        data = {}
        
        try:
            # Load price data
            price_path = f"{RAW_DATA_DIR}/{ticker}_prices.csv"
            if os.path.exists(price_path):
                data['prices'] = pd.read_csv(price_path, index_col=0, parse_dates=True)
            
            # Load earnings calendar
            calendar_path = f"{RAW_DATA_DIR}/{ticker}_earnings_calendar.csv"
            if os.path.exists(calendar_path):
                data['earnings_calendar'] = pd.read_csv(calendar_path, index_col=0)
            
            # Load historical earnings
            earnings_path = f"{RAW_DATA_DIR}/{ticker}_historical_earnings.csv"
            if os.path.exists(earnings_path):
                data['historical_earnings'] = pd.read_csv(earnings_path, index_col=0)
                
            return data
            
        except Exception as e:
            logger.error(f"Error loading data for {ticker}: {str(e)}")
            return {}
    
    def process_earnings_impact(self, ticker: str) -> Optional[pd.DataFrame]:
        """Analyze the impact of earnings announcements on stock price."""
        try:
            data = self.load_raw_data(ticker)
            
            if 'prices' not in data or 'historical_earnings' not in data:
                logger.warning(f"Insufficient data for earnings impact analysis for {ticker}")
                return None
            
            prices = data['prices']
            earnings = data['historical_earnings']
            
            # Convert earnings index to datetime
            if not isinstance(earnings.index, pd.DatetimeIndex):
                earnings.index = pd.to_datetime(earnings.index)
            
            # Initialize results
            results = []
            
            # Analyze each earnings date
            for earnings_date in earnings.index:
                # Skip if no price data for this date
                if earnings_date not in prices.index:
                    continue
                
                # Get price data around earnings date
                start_date = (earnings_date - pd.Timedelta(days=5)).strftime('%Y-%m-%d')
                end_date = (earnings_date + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
                
                # Get price data for the window
                mask = (prices.index >= start_date) & (prices.index <= end_date)
                window = prices.loc[mask].copy()
                
                if window.empty:
                    continue
                
                # Calculate returns
                window['returns'] = window['Close'].pct_change() * 100
                
                # Get pre and post-earnings returns
                pre_earnings = window[window.index < earnings_date]
                post_earnings = window[window.index >= earnings_date]
                
                if pre_earnings.empty or post_earnings.empty:
                    continue
                
                # Calculate metrics
                result = {
                    'ticker': ticker,
                    'earnings_date': earnings_date,
                    'pre_avg_return': pre_earnings['returns'].mean(),
                    'post_avg_return': post_earnings['returns'].mean(),
                    'pre_volatility': pre_earnings['returns'].std(),
                    'post_volatility': post_earnings['returns'].std(),
                    'earnings_surprise': earnings.loc[earnings_date, 'Earnings'] if 'Earnings' in earnings.columns else np.nan,
                    'price_reaction': (post_earnings['Close'].iloc[0] / pre_earnings['Close'].iloc[-1] - 1) * 100
                }
                
                results.append(result)
            
            if not results:
                return None
                
            # Create and save results
            results_df = pd.DataFrame(results)
            results_df.to_csv(f"{PROCESSED_DATA_DIR}/{ticker}_earnings_impact.csv")
            
            return results_df
            
        except Exception as e:
            logger.error(f"Error processing earnings impact for {ticker}: {str(e)}")
            return None
    
    def process_all_tickers(self, tickers: List[str] = None) -> None:
        """Process data for all tickers."""
        tickers = tickers or DEFAULT_TICKERS
        
        for ticker in tickers:
            logger.info(f"Processing data for {ticker}...")
            self.process_earnings_impact(ticker)

def main():
    """Main function to run data processing."""
    logger.info("Starting data processing...")
    
    processor = DataProcessor()
    processor.process_all_tickers()
    
    logger.info("Data processing complete!")

if __name__ == "__main__":
    main()
