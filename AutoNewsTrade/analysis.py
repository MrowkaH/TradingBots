"""
Analysis module for AutoNewsTrade.
Provides visualization and statistical analysis of the processed data.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional
import logging

from config import PROCESSED_DATA_DIR, DEFAULT_TICKERS

# Set up plotting style
plt.style.use('seaborn')
sns.set_palette('viridis')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EarningsAnalyzer:
    """Class for analyzing earnings data and generating insights."""
    
    def __init__(self):
        self.results = {}
    
    def load_processed_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Load processed data for a given ticker."""
        file_path = f"{PROCESSED_DATA_DIR}/{ticker}_earnings_impact.csv"
        
        if not os.path.exists(file_path):
            logger.warning(f"No processed data found for {ticker}")
            return None
        
        try:
            df = pd.read_csv(file_path, parse_dates=['earnings_date'], index_col=0)
            self.results[ticker] = df
            return df
        except Exception as e:
            logger.error(f"Error loading processed data for {ticker}: {str(e)}")
            return None
    
    def plot_earnings_impact(self, ticker: str, save_path: str = None) -> None:
        """Plot the impact of earnings announcements on stock price."""
        if ticker not in self.results:
            df = self.load_processed_data(ticker)
            if df is None or df.empty:
                return
        else:
            df = self.results[ticker]
        
        plt.figure(figsize=(12, 6))
        
        # Plot price reaction
        plt.subplot(1, 2, 1)
        sns.histplot(df['price_reaction'], kde=True, bins=15)
        plt.axvline(0, color='red', linestyle='--', alpha=0.5)
        plt.title(f'{ticker} - Price Reaction to Earnings')
        plt.xlabel('Price Change (%)')
        plt.ylabel('Frequency')
        
        # Plot pre vs post volatility
        plt.subplot(1, 2, 2)
        sns.scatterplot(
            x=df['pre_volatility'],
            y=df['post_volatility'],
            hue=df['price_reaction'] > 0,
            palette={True: 'green', False: 'red'},
            alpha=0.7
        )
        plt.plot([0, max(df[['pre_volatility', 'post_volatility']].max())], 
                 [0, max(df[['pre_volatility', 'post_volatility']].max())], 
                 'r--', alpha=0.3)
        plt.title('Volatility Before vs After Earnings')
        plt.xlabel('Pre-Earnings Volatility (%)')
        plt.ylabel('Post-Earnings Volatility (%)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def analyze_earnings_strategy(self, ticker: str) -> Dict:
        """Analyze a simple earnings-based trading strategy.
        
        Strategy: Buy before earnings, sell after X days if price increases by Y%
        """
        if ticker not in self.results:
            df = self.load_processed_data(ticker)
            if df is None or df.empty:
                return {}
        else:
            df = self.results[ticker]
        
        if df.empty:
            return {}
        
        # Simple strategy: Buy 1 day before earnings, sell 1 day after
        df['strategy_return'] = df['price_reaction']
        
        # Calculate metrics
        win_rate = (df['strategy_return'] > 0).mean() * 100
        avg_return = df['strategy_return'].mean()
        avg_positive = df[df['strategy_return'] > 0]['strategy_return'].mean()
        avg_negative = df[df['strategy_return'] <= 0]['strategy_return'].mean()
        
        results = {
            'ticker': ticker,
            'num_earnings': len(df),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'avg_positive_return': avg_positive,
            'avg_negative_return': avg_negative,
            'sharpe_ratio': df['strategy_return'].mean() / (df['strategy_return'].std() + 1e-8),
            'max_drawdown': (df['strategy_return'].cumsum() - df['strategy_return'].cumsum().cummax()).min()
        }
        
        return results
    
    def analyze_all_tickers(self, tickers: List[str] = None) -> pd.DataFrame:
        """Analyze all tickers and return a summary."""
        tickers = tickers or DEFAULT_TICKERS
        results = []
        
        for ticker in tickers:
            logger.info(f"Analyzing {ticker}...")
            if ticker not in self.results:
                self.load_processed_data(ticker)
            
            result = self.analyze_earnings_strategy(ticker)
            if result:
                results.append(result)
        
        if not results:
            return pd.DataFrame()
        
        # Create and save summary
        summary = pd.DataFrame(results)
        summary.to_csv(f"{PROCESSED_DATA_DIR}/strategy_summary.csv")
        
        return summary
    
    def plot_summary(self, summary: pd.DataFrame) -> None:
        """Plot summary statistics for all tickers."""
        if summary.empty:
            logger.warning("No data to plot")
            return
        
        plt.figure(figsize=(15, 10))
        
        # Sort by average return
        summary = summary.sort_values('avg_return', ascending=False)
        
        # Plot win rates and average returns
        plt.subplot(2, 1, 1)
        ax = summary.set_index('ticker')['win_rate'].plot(kind='bar')
        plt.title('Win Rate by Ticker')
        plt.ylabel('Win Rate (%)')
        plt.xticks(rotation=45)
        
        # Add value labels
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.1f}%", 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', xytext=(0, 5), 
                       textcoords='offset points')
        
        plt.subplot(2, 1, 2)
        ax = summary.set_index('ticker')['avg_return'].plot(kind='bar', color='orange')
        plt.title('Average Return by Ticker')
        plt.ylabel('Average Return (%)')
        plt.xticks(rotation=45)
        
        # Add value labels
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.2f}%", 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', xytext=(0, 5), 
                       textcoords='offset points')
        
        plt.tight_layout()
        plt.show()

def main():
    """Main function to run analysis."""
    logger.info("Starting analysis...")
    
    analyzer = EarningsAnalyzer()
    
    # Analyze all tickers
    summary = analyzer.analyze_all_tickers()
    
    if not summary.empty:
        # Print summary
        print("\nStrategy Performance Summary:")
        print(summary[['ticker', 'win_rate', 'avg_return', 'sharpe_ratio']].to_string())
        
        # Plot summary
        analyzer.plot_summary(summary)
        
        # Plot individual ticker analysis
        for ticker in summary['ticker'].head(3):  # Plot top 3 tickers
            analyzer.plot_earnings_impact(ticker, f"{PROCESSED_DATA_DIR}/{ticker}_analysis.png")
    
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main()
