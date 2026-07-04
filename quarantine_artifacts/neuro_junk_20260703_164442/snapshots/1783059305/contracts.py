"""
L2 DOMAIN CONTRACTS

NO LOGIC — ONLY INTERFACES
"""

class StrategyContract:
    def generate_signal(self, data): raise NotImplementedError

class RiskContract:
    def evaluate(self, order): raise NotImplementedError

class PortfolioContract:
    def allocate(self, signal): raise NotImplementedError
