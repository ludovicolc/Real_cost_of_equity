import yfinance as yf
import numpy as np

class Company_info:
    def __init__(self, company_ticker: str):
        self.company_ticker = company_ticker

        # Collecting company information
        self.ticker = yf.Ticker(self.company_ticker)
        self.name = self.ticker.info['shortName']
        self.industry = self.ticker.info['industry']
        self.beta = self.ticker.info['beta']
        self.debt = self.ticker.info['totalDebt']
        self.market_cap = self.ticker.fast_info['marketCap']
        self.debt_equity = self.debt / self.market_cap
        
        # Tax rate (3 year average)
        income_statements = list(self.ticker.get_incomestmt(as_dict=True).items())
        tax_rates = []
        for year in range(3):
            tax_rates.append(income_statements[year][1]['TaxRateForCalcs'])
        self.mean_tax_rate = np.mean(tax_rates)
        
        self.unlevered_beta = self.calculate_unlevered_beta()
        
    def calculate_unlevered_beta(self):
        self.unlevered_beta = self.beta / (1 + (self.debt_equity * (1 - self.mean_tax_rate)))
        return self.unlevered_beta

    def calculate_levered_beta(self, unlevered_betas: list):
        levered_beta = round(np.mean(unlevered_betas) * (1 + (self.debt_equity * (1 - self.mean_tax_rate))), 2)
        return levered_beta