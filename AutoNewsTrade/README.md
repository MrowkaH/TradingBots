# AutoNewsTrade

AutoNewsTrade is a Python-based framework for analyzing the impact of earnings announcements on stock prices. The goal is to identify patterns and potential trading opportunities around these events.

## Features

- **Data Collection**: Fetches historical price data and earnings information for given tickers
- **Data Processing**: Analyzes the impact of earnings announcements on stock prices
- **Strategy Analysis**: Evaluates simple trading strategies based on earnings announcements
- **Visualization**: Generates insightful visualizations of earnings impact and strategy performance

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (install via `pip install -r requirements.txt`)
- [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key) (for additional data)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/autonewstrade.git
   cd autonewstrade
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Alpha Vantage API key (optional but recommended):
   ```bash
   # On Windows
   setx ALPHA_VANTAGE_API_KEY "your_api_key_here"
   
   # On macOS/Linux
   export ALPHA_VANTAGE_API_KEY="your_api_key_here"
   ```

## Usage

1. **Collect Data**
   ```bash
   python data_collection.py
   ```
   This will download historical price and earnings data for the default tickers.

2. **Process Data**
   ```bash
   python data_processing.py
   ```
   This processes the raw data and calculates earnings impact metrics.

3. **Run Analysis**
   ```bash
   python analysis.py
   ```
   This generates visualizations and performance metrics for the analyzed tickers.

## Project Structure

```
autonewstrade/
├── config.py              # Configuration settings
├── data_collection.py     # Data collection module
├── data_processing.py     # Data processing and analysis
├── analysis.py            # Visualization and strategy analysis
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Example Output

The analysis will generate several output files in the `data/processed/` directory, including:
- `{ticker}_earnings_impact.csv`: Detailed earnings impact data for each ticker
- `strategy_summary.csv`: Summary of strategy performance across all tickers
- `{ticker}_analysis.png`: Visualization of earnings impact for individual tickers

## Customization

You can modify the default settings in `config.py`:
- Add/remove tickers from the `DEFAULT_TICKERS` list
- Adjust date ranges for historical data
- Configure data directories

## Limitations

- This is for educational purposes only, not financial advice
- Past performance is not indicative of future results
- The default strategy is simple and may not be profitable
- Consider transaction costs, slippage, and other real-world factors in live trading

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
