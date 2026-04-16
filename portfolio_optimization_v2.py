import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# MODERN PORTFOLIO THEORY - EFFICIENT FRONTIER OPTIMIZATION
# With Synthetic Data for Offline Use
# ============================================================================

class PortfolioOptimizer:
    def __init__(self, tickers, returns_data, cov_matrix, risk_free_rate=0.03):
        """Initialize portfolio optimizer with pre-computed returns and covariance"""
        self.tickers = tickers
        self.mean_returns = returns_data  # Annualized
        self.cov_matrix = cov_matrix       # Annualized
        self.risk_free_rate = risk_free_rate
        
        print(f"✓ Portfolio initialized with {len(tickers)} assets")
        print(f"✓ Mean Returns (annual): {self.mean_returns}")
        print(f"✓ Risk-Free Rate: {risk_free_rate*100:.2f}%\n")
    
    def portfolio_performance(self, weights):
        """Calculate portfolio return and volatility using linear algebra"""
        # Return: R_p = w^T * μ (dot product of weights and mean returns)
        portfolio_return = np.dot(weights, self.mean_returns)
        
        # Volatility: σ_p = sqrt(w^T * Σ * w) (quadratic form)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        return portfolio_return, portfolio_volatility
    
    def negative_sharpe(self, weights):
        """Negative Sharpe Ratio for minimization: -(R_p - R_f) / σ_p"""
        p_ret, p_vol = self.portfolio_performance(weights)
        return -(p_ret - self.risk_free_rate) / (p_vol + 1e-9)
    
    def portfolio_volatility(self, weights):
        """Return portfolio volatility for minimum variance optimization"""
        return self.portfolio_performance(weights)[1]
    
    def generate_random_portfolios(self, num_portfolios=10000):
        """Generate random portfolios for visualization"""
        results = np.zeros((3, num_portfolios))
        
        print(f"🎲 Generating {num_portfolios:,} random portfolios...")
        
        for i in range(num_portfolios):
            # Random weights with Dirichlet distribution
            weights = np.random.dirichlet(np.ones(len(self.tickers)))
            
            ret, vol = self.portfolio_performance(weights)
            sharpe = (ret - self.risk_free_rate) / (vol + 1e-9)
            
            results[0, i] = vol
            results[1, i] = ret
            results[2, i] = sharpe
        
        return results
    
    def optimize_portfolio(self, optimization_type='sharpe'):
        """Optimize portfolio weights using constrained optimization"""
        num_assets = len(self.tickers)
        init_guess = np.array([1/num_assets] * num_assets)
        
        # Constraint: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        # Bounds: weights between 0 and 1 (no short selling)
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        if optimization_type == 'sharpe':
            result = minimize(self.negative_sharpe, init_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints,
                            options={'ftol': 1e-9})
        else:  # min_variance
            result = minimize(self.portfolio_volatility, init_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints,
                            options={'ftol': 1e-9})
        
        return result.x
    
    def efficient_frontier_portfolios(self, num_portfolios=100):
        """Generate efficient frontier by varying target return"""
        # Get return range
        min_ret = self.mean_returns.min()
        max_ret = self.mean_returns.max()
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        efficient_vols = []
        efficient_weights = []
        
        print(f"📈 Calculating efficient frontier ({num_portfolios} points)...")
        
        for i, target_ret in enumerate(target_returns):
            if (i + 1) % 25 == 0:
                print(f"  Progress: {i+1}/{num_portfolios}")
            
            constraints = (
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w: np.dot(w, self.mean_returns) - target_ret}
            )
            bounds = tuple((0, 1) for _ in range(len(self.tickers)))
            init_guess = np.array([1/len(self.tickers)] * len(self.tickers))
            
            result = minimize(self.portfolio_volatility, init_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints,
                            options={'ftol': 1e-9})
            
            if result.success:
                efficient_vols.append(result.fun)
                efficient_weights.append(result.x)
        
        return target_returns[:len(efficient_vols)], np.array(efficient_vols)
    
    def plot_efficient_frontier(self, random_portfolios_num=5000):
        """Plot the Efficient Frontier with optimal portfolios"""
        # Generate random portfolios
        random_results = self.generate_random_portfolios(random_portfolios_num)
        
        # Calculate Efficient Frontier
        ef_returns, ef_volatility = self.efficient_frontier_portfolios(100)
        
        # Optimize for Max Sharpe Ratio
        print("⚡ Optimizing Maximum Sharpe Ratio portfolio...")
        max_sharpe_weights = self.optimize_portfolio('sharpe')
        max_sharpe_return, max_sharpe_vol = self.portfolio_performance(max_sharpe_weights)
        max_sharpe_ratio = (max_sharpe_return - self.risk_free_rate) / max_sharpe_vol
        
        # Optimize for Minimum Variance
        print("⚡ Optimizing Minimum Variance portfolio...")
        min_var_weights = self.optimize_portfolio('min_variance')
        min_var_return, min_var_vol = self.portfolio_performance(min_var_weights)
        
        # Create comprehensive figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
        
        # ===== LEFT PLOT: Efficient Frontier =====
        scatter = ax1.scatter(random_results[0], random_results[1], 
                             c=random_results[2], cmap='viridis', 
                             alpha=0.3, s=20, label='Random Portfolios')
        
        # Plot Efficient Frontier
        ax1.plot(ef_volatility, ef_returns, 'r-', linewidth=3.5, label='Efficient Frontier', zorder=4)
        
        # Plot optimal portfolios
        ax1.scatter(max_sharpe_vol, max_sharpe_return, marker='*', color='gold', 
                   s=1500, edgecolor='red', linewidth=2.5, label='Max Sharpe Ratio', zorder=5)
        ax1.scatter(min_var_vol, min_var_return, marker='s', color='blue',
                   s=250, edgecolor='darkblue', linewidth=2, label='Min Variance', zorder=5)
        ax1.scatter(0, self.risk_free_rate, marker='o', color='green', s=350,
                   edgecolor='darkgreen', linewidth=2, label='Risk-Free Asset', zorder=5)
        
        # Capital Allocation Line
        cal_x = np.array([0, max_sharpe_vol * 1.5])
        cal_y = self.risk_free_rate + max_sharpe_ratio * cal_x
        ax1.plot(cal_x, cal_y, 'g--', linewidth=2.5, alpha=0.8, label='Capital Allocation Line', zorder=3)
        
        ax1.set_xlabel('Volatility (Risk) σ', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Expected Annual Return μ', fontsize=12, fontweight='bold')
        ax1.set_title('Modern Portfolio Theory - Efficient Frontier', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=10, framealpha=0.95)
        ax1.grid(True, alpha=0.3, linestyle='--')
        cbar = plt.colorbar(scatter, ax=ax1)
        cbar.set_label('Sharpe Ratio', fontsize=10)
        
        # ===== RIGHT PLOT: Portfolio Allocation =====
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.tickers)))
        
        # Max Sharpe Ratio portfolio
        ax2.barh([i for i in range(len(self.tickers))], max_sharpe_weights, 
                color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
        ax2.set_yticks(range(len(self.tickers)))
        ax2.set_yticklabels(self.tickers, fontweight='bold')
        ax2.set_xlabel('Portfolio Weight', fontsize=11, fontweight='bold')
        ax2.set_title('Maximum Sharpe Ratio Portfolio Allocation', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add percentage labels
        for i, (ticker, weight) in enumerate(zip(self.tickers, max_sharpe_weights)):
            if weight > 0.01:
                ax2.text(weight + 0.01, i, f'{weight*100:.1f}%', 
                        va='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/efficient_frontier.png', dpi=300, bbox_inches='tight')
        print("\n✓ Efficient Frontier plot saved!\n")
        plt.show()
        
        return max_sharpe_weights, max_sharpe_return, max_sharpe_vol, min_var_weights
    
    def print_portfolio_details(self, weights, portfolio_name):
        """Print detailed portfolio analysis"""
        ret, vol = self.portfolio_performance(weights)
        sharpe = (ret - self.risk_free_rate) / vol
        
        print(f"\n{'='*70}")
        print(f"📋 {portfolio_name}")
        print(f"{'='*70}")
        print(f"Expected Annual Return:  {ret*100:>8.2f}%")
        print(f"Annual Volatility (Risk):{vol*100:>8.2f}%")
        print(f"Sharpe Ratio:            {sharpe:>8.3f}")
        print(f"\n{'Asset':<10} {'Weight':>10} {'Return':>10} {'Volatility':>12}")
        print("-" * 70)
        
        for i, ticker in enumerate(self.tickers):
            weight = weights[i]
            individual_return = self.mean_returns[i]
            individual_vol = np.sqrt(self.cov_matrix[i, i])
            print(f"{ticker:<10} {weight*100:>9.2f}% {individual_return*100:>9.2f}% {individual_vol*100:>11.2f}%")
        
        print("-" * 70)
        print(f"{'Total':<10} {np.sum(weights)*100:>9.2f}%")


# ============================================================================
# SYNTHETIC DATA GENERATION
# ============================================================================

def generate_synthetic_portfolio_data(num_assets=6, num_days=252*4):
    """Generate realistic synthetic stock returns data"""
    np.random.seed(42)
    
    # Mean annual returns (realistic tech stock range: 10-30%)
    mean_returns = np.array([0.15, 0.18, 0.14, 0.22, 0.20, 0.12])
    
    # Create realistic correlation structure
    correlations = np.array([
        [1.00, 0.65, 0.68, 0.55, 0.45, 0.60],
        [0.65, 1.00, 0.72, 0.58, 0.50, 0.65],
        [0.68, 0.72, 1.00, 0.62, 0.48, 0.68],
        [0.55, 0.58, 0.62, 1.00, 0.52, 0.55],
        [0.45, 0.50, 0.48, 0.52, 1.00, 0.45],
        [0.60, 0.65, 0.68, 0.55, 0.45, 1.00]
    ])
    
    # Individual volatilities (annual): 15-35%
    volatilities = np.array([0.25, 0.28, 0.22, 0.32, 0.35, 0.20])
    
    # Construct covariance matrix: Σ = D * R * D (D is diagonal of vols)
    cov_matrix = np.outer(volatilities, volatilities) * correlations
    
    # Daily volatilities (assuming 252 trading days)
    daily_cov = cov_matrix / 252
    daily_mean = mean_returns / 252
    
    # Generate synthetic returns
    returns = np.random.multivariate_normal(daily_mean, daily_cov, num_days)
    
    # Annualize for output
    annualized_returns = mean_returns
    annualized_cov = cov_matrix
    
    return annualized_returns, annualized_cov


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Define assets (tech stocks)
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TESLA', 'META']
    
    # Generate synthetic data
    print("🔬 Generating synthetic portfolio data...")
    mean_returns, cov_matrix = generate_synthetic_portfolio_data(len(tickers))
    
    # Create optimizer
    optimizer = PortfolioOptimizer(
        tickers=tickers,
        returns_data=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=0.03
    )
    
    # Display correlation matrix
    print("\n📊 CORRELATION MATRIX")
    print("=" * 70)
    corr_df = pd.DataFrame(
        cov_matrix / np.outer(np.sqrt(np.diag(cov_matrix)), np.sqrt(np.diag(cov_matrix))),
        index=tickers,
        columns=tickers
    )
    print(corr_df.round(3))
    
    # Generate and plot Efficient Frontier
    print("\n" + "="*70)
    print("🚀 EFFICIENT FRONTIER OPTIMIZATION")
    print("="*70)
    
    max_sharpe_w, max_sharpe_r, max_sharpe_v, min_var_w = optimizer.plot_efficient_frontier(5000)
    
    # Print detailed portfolio analysis
    optimizer.print_portfolio_details(max_sharpe_w, "MAXIMUM SHARPE RATIO PORTFOLIO")
    optimizer.print_portfolio_details(min_var_w, "MINIMUM VARIANCE PORTFOLIO")
    
    # Summary comparison
    min_var_ret, min_var_vol = optimizer.portfolio_performance(min_var_w)
    min_var_sharpe = (min_var_ret - optimizer.risk_free_rate) / min_var_vol
    max_sharpe_ratio = (max_sharpe_r - optimizer.risk_free_rate) / max_sharpe_v
    
    print(f"\n{'='*70}")
    print("📈 PORTFOLIO COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"{'Metric':<25} {'Max Sharpe':>15} {'Min Variance':>15}")
    print("-" * 70)
    print(f"{'Expected Return':<25} {max_sharpe_r*100:>14.2f}% {min_var_ret*100:>14.2f}%")
    print(f"{'Volatility (Risk)':<25} {max_sharpe_v*100:>14.2f}% {min_var_vol*100:>14.2f}%")
    print(f"{'Sharpe Ratio':<25} {max_sharpe_ratio:>15.3f} {min_var_sharpe:>15.3f}")
    print(f"{'Return/Risk Ratio':<25} {max_sharpe_r/max_sharpe_v:>15.3f} {min_var_ret/min_var_vol:>15.3f}")
    print("=" * 70)
