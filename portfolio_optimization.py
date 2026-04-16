import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# MODERN PORTFOLIO THEORY - EFFICIENT FRONTIER OPTIMIZATION
# ============================================================================

class PortfolioOptimizer:
    def __init__(self, tickers, start_date='2021-01-01', end_date='2024-01-01', risk_free_rate=0.02):
        """Initialize portfolio optimizer with stock tickers"""
        self.tickers = tickers
        self.risk_free_rate = risk_free_rate
        
        # Fetch historical data
        print(f"📊 Fetching data for {len(tickers)} stocks...")
        self.data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
        
        # Calculate daily returns
        self.returns = self.data.pct_change().dropna()
        self.mean_returns = self.returns.mean() * 252  # Annualized
        self.cov_matrix = self.returns.cov() * 252      # Annualized
        
        print(f"✓ Data loaded: {len(self.returns)} trading days")
        print(f"✓ Annualized Returns: {self.mean_returns.values}")
        print(f"✓ Covariance Matrix calculated\n")
    
    def portfolio_performance(self, weights):
        """Calculate portfolio return and volatility"""
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        return portfolio_return, portfolio_volatility
    
    def negative_sharpe(self, weights):
        """Negative Sharpe Ratio (for minimization)"""
        p_ret, p_vol = self.portfolio_performance(weights)
        return -(p_ret - self.risk_free_rate) / p_vol
    
    def portfolio_volatility(self, weights):
        """Portfolio volatility for minimum variance optimization"""
        return self.portfolio_performance(weights)[1]
    
    def generate_random_portfolios(self, num_portfolios=10000):
        """Generate random portfolios for visualization"""
        results = np.zeros((3, num_portfolios))
        
        for i in range(num_portfolios):
            weights = np.random.random(len(self.tickers))
            weights /= np.sum(weights)  # Normalize
            
            ret, vol = self.portfolio_performance(weights)
            sharpe = (ret - self.risk_free_rate) / vol
            
            results[0,i] = vol
            results[1,i] = ret
            results[2,i] = sharpe
        
        return results
    
    def optimize_portfolio(self, optimization_type='sharpe'):
        """Optimize portfolio weights"""
        num_assets = len(self.tickers)
        init_guess = np.array([1/num_assets] * num_assets)
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        if optimization_type == 'sharpe':
            result = minimize(self.negative_sharpe, init_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints)
        else:  # min_variance
            result = minimize(self.portfolio_volatility, init_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints)
        
        return result.x
    
    def efficient_frontier_portfolios(self, num_portfolios=100):
        """Generate efficient frontier by varying target return"""
        min_ret = self.mean_returns.min()
        max_ret = self.mean_returns.max()
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        efficient_vols = []
        efficient_weights = []
        
        for target_ret in target_returns:
            constraints = (
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w: np.sum(self.mean_returns * w) - target_ret}
            )
            bounds = tuple((0, 1) for _ in range(len(self.tickers)))
            init_guess = np.array([1/len(self.tickers)] * len(self.tickers))
            
            result = minimize(self.portfolio_volatility, init_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints)
            
            if result.success:
                efficient_vols.append(result.fun)
                efficient_weights.append(result.x)
        
        return target_returns[:len(efficient_vols)], np.array(efficient_vols)
    
    def plot_efficient_frontier(self, random_portfolios_num=5000):
        """Plot the Efficient Frontier with optimal portfolios"""
        print("🔄 Generating random portfolios for visualization...")
        random_results = self.generate_random_portfolios(random_portfolios_num)
        
        print("📈 Calculating Efficient Frontier...")
        ef_returns, ef_volatility = self.efficient_frontier_portfolios(100)
        
        print("⚡ Optimizing Max Sharpe Ratio portfolio...")
        max_sharpe_weights = self.optimize_portfolio('sharpe')
        max_sharpe_return, max_sharpe_vol = self.portfolio_performance(max_sharpe_weights)
        max_sharpe_ratio = (max_sharpe_return - self.risk_free_rate) / max_sharpe_vol
        
        print("⚡ Optimizing Minimum Variance portfolio...")
        min_var_weights = self.optimize_portfolio('min_variance')
        min_var_return, min_var_vol = self.portfolio_performance(min_var_weights)
        
        # Create figure
        plt.figure(figsize=(14, 9))
        
        # Plot random portfolios
        plt.scatter(random_results[0], random_results[1], c=random_results[2],
                   cmap='viridis', alpha=0.3, s=10, label='Random Portfolios')
        
        # Plot Efficient Frontier
        plt.plot(ef_volatility, ef_returns, 'r-', linewidth=3, label='Efficient Frontier')
        
        # Plot optimal portfolios
        plt.scatter(max_sharpe_vol, max_sharpe_return, marker='*', color='gold', 
                   s=1000, edgecolor='red', linewidth=2, label=f'Max Sharpe ({max_sharpe_ratio:.2f})', zorder=5)
        plt.scatter(min_var_vol, min_var_return, marker='s', color='blue',
                   s=200, edgecolor='darkblue', linewidth=2, label='Min Variance', zorder=5)
        
        # Add Capital Allocation Line (CAL)
        cal_x = np.array([0, max_sharpe_vol * 1.5])
        cal_y = self.risk_free_rate + max_sharpe_ratio * cal_x
        plt.plot(cal_x, cal_y, 'g--', linewidth=2, alpha=0.7, label='Capital Allocation Line')
        
        # Plot risk-free asset
        plt.scatter(0, self.risk_free_rate, marker='o', color='green', s=300,
                   edgecolor='darkgreen', linewidth=2, label='Risk-Free Asset', zorder=5)
        
        # Labels and formatting
        plt.xlabel('Volatility (Standard Deviation)', fontsize=12, fontweight='bold')
        plt.ylabel('Expected Annual Return', fontsize=12, fontweight='bold')
        plt.title('Efficient Frontier - Modern Portfolio Theory', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=10, framealpha=0.9)
        plt.colorbar(label='Sharpe Ratio')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save and show
        plt.savefig('/mnt/user-data/outputs/efficient_frontier.png', dpi=300, bbox_inches='tight')
        print("\n✓ Efficient Frontier plot saved!")
        plt.show()
        
        return max_sharpe_weights, max_sharpe_return, max_sharpe_vol, min_var_weights
    
    def print_portfolio_details(self, weights, portfolio_name):
        """Print detailed portfolio allocation"""
        ret, vol = self.portfolio_performance(weights)
        sharpe = (ret - self.risk_free_rate) / vol
        
        print(f"\n{'='*60}")
        print(f"📋 {portfolio_name}")
        print(f"{'='*60}")
        print(f"Expected Annual Return: {ret*100:.2f}%")
        print(f"Annual Volatility (Risk): {vol*100:.2f}%")
        print(f"Sharpe Ratio: {sharpe:.3f}")
        print(f"\nOptimal Weights:")
        for ticker, weight in zip(self.tickers, weights):
            if weight > 0.01:
                print(f"  {ticker}: {weight*100:6.2f}%")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Select tech stocks for portfolio
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TESLA', 'META']
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer(
        tickers=tickers,
        start_date='2020-01-01',
        end_date='2024-01-01',
        risk_free_rate=0.03
    )
    
    # Generate Efficient Frontier and optimize
    max_sharpe_w, max_sharpe_r, max_sharpe_v, min_var_w = optimizer.plot_efficient_frontier(5000)
    
    # Print portfolio details
    optimizer.print_portfolio_details(max_sharpe_w, "Maximum Sharpe Ratio Portfolio")
    optimizer.print_portfolio_details(min_var_w, "Minimum Variance Portfolio")
    
    # Summary statistics
    print(f"\n{'='*60}")
    print("📊 PORTFOLIO COMPARISON")
    print(f"{'='*60}")
    print(f"Risk-Free Rate: {optimizer.risk_free_rate*100:.2f}%")
    print(f"Individual Stock Returns: {optimizer.mean_returns.values}")
    print(f"Individual Stock Volatilities: {np.sqrt(np.diag(optimizer.cov_matrix))}")
