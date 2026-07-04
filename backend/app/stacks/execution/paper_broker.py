"""AUTO GENERATED RUNTIME FILE"""

from stacks.portfolio.rebalance import execute_trade  # Import the execute_trade function
from stacks.journal_ledger.ledger import save_log  # Import the save_log function

def healthcheck():
    return {"status": "ok"}

def process_portfolio_output(portfolio_output: dict):
    if 'signal' in portfolio_output and 'symbol' in portfolio_output:
        signal = portfolio_output['signal']
        symbol = portfolio_output['symbol']
        
        trade_result = execute_trade(symbol, signal)  # Call the execute_trade function
        save_log(trade_result)  # Save the log using journal_ledger/ledger.py
