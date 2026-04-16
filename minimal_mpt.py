"""
Modern Portfolio Theory - Minimal Implementation (60 lines)
Linear Algebra-based Efficient Frontier Construction
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# ============== 1. SYNTHETIC DATA ==============
np.random.seed(42)
n_assets = 6
mean_returns = np.array([0.15, 0.18, 0.14, 0.22, 0.20, 0.12])
volatilities = np.array([0.25, 0.28, 0.22, 0.32, 0.35, 0.20])
correlations = np.array([
    [1.00, 0.65, 0.68, 0.55, 0.45, 0.60],
    [0.65, 1.00, 0.72, 0.58, 0.50, 0.65],
    [0.68, 0.72, 1.00, 0.62, 0.48, 0.68],
    [0.55, 0.58, 0.62, 1.00, 0.52, 0.55],
    [0.45, 0.50, 0.48, 0.52, 1.00, 0.45],
    [0.60, 0.65, 0.68, 0.55, 0.45, 1.00]
])
cov_matrix = np.outer(volatilities, volatilities) * correlations
rf_rate = 0.03

# ============== 2. LINEAR ALGEBRA FUNCTIONS ==============
def portfolio_return(w):
    """R_p = w^T · μ"""
    return np.dot(w, mean_returns)

def portfolio_volatility(w):
    """σ_p = √(w^T · Σ · w)"""
    return np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))

def sharpe_ratio(w):
    """SR = (R_p - R_f) / σ_p"""
    return (portfolio_return(w) - rf_rate) / portfolio_volatility(w)

# ============== 3. OPTIMIZATION ==============
def optimize(objective_func):
    """Minimize objective with constraints: Σwᵢ=1, 0≤wᵢ≤1"""
    w0 = np.ones(n_assets) / n_assets
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    result = minimize(objective_func, w0, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

# Max Sharpe Ratio Portfolio
w_sharpe = optimize(lambda w: -sharpe_ratio(w))  # Negative for minimization
ret_sharpe = portfolio_return(w_sharpe)
vol_sharpe = portfolio_volatility(w_sharpe)

# Min Variance Portfolio
w_minvar = optimize(portfolio_volatility)
ret_minvar = portfolio_return(w_minvar)
vol_minvar = portfolio_volatility(w_minvar)

# ============== 4. EFFICIENT FRONTIER ==============
ef_vols, ef_rets = [], []
w0 = np.ones(n_assets) / n_assets
target_rets = np.linspace(mean_returns.min(), mean_returns.max(), 100)
for r_target in target_rets:
    constraints = (
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'eq', 'fun': lambda w: portfolio_return(w) - r_target}
    )
    result = minimize(portfolio_volatility, w0, method='SLSQP', 
                     bounds=tuple((0, 1) for _ in range(n_assets)), 
                     constraints=constraints)
    if result.success:
        ef_vols.append(result.fun)
        ef_rets.append(r_target)

# ============== 5. RANDOM PORTFOLIOS (for visualization) ==============
n_random = 5000
random_rets, random_vols, random_sharpes = [], [], []
for _ in range(n_random):
    w = np.random.dirichlet(np.ones(n_assets))
    random_rets.append(portfolio_return(w))
    random_vols.append(portfolio_volatility(w))
    random_sharpes.append((portfolio_return(w) - rf_rate) / portfolio_volatility(w))

# ============== 6. VISUALIZATION ==============
plt.figure(figsize=(14, 8))
plt.scatter(random_vols, random_rets, c=random_sharpes, cmap='viridis', 
           alpha=0.3, s=10, label='Random Portfolios')
plt.plot(ef_vols, ef_rets, 'r-', linewidth=3, label='Efficient Frontier')
plt.scatter([vol_sharpe], [ret_sharpe], marker='*', color='gold', s=1500, 
           edgecolor='red', linewidth=2, label='Max Sharpe Ratio', zorder=5)
plt.scatter([vol_minvar], [ret_minvar], marker='s', color='blue', s=250, 
           edgecolor='darkblue', linewidth=2, label='Min Variance', zorder=5)
plt.scatter([0], [rf_rate], marker='o', color='green', s=350, 
           edgecolor='darkgreen', linewidth=2, label='Risk-Free Asset', zorder=5)

# Capital Allocation Line
cal_x = np.array([0, max(ef_vols) * 1.5])
cal_y = rf_rate + (ret_sharpe - rf_rate) / vol_sharpe * cal_x
plt.plot(cal_x, cal_y, 'g--', linewidth=2.5, alpha=0.8, label='Capital Allocation Line')

plt.xlabel('Volatility (σ)', fontsize=12, fontweight='bold')
plt.ylabel('Expected Return (μ)', fontsize=12, fontweight='bold')
plt.title('Efficient Frontier - Modern Portfolio Theory', fontsize=14, fontweight='bold')
plt.legend(loc='upper left', fontsize=10)
plt.colorbar(label='Sharpe Ratio')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/efficient_frontier_minimal.png', dpi=300, bbox_inches='tight')
plt.show()

# ============== 7. RESULTS ==============
print("\n" + "="*70)
print("MAXIMUM SHARPE RATIO PORTFOLIO")
print("="*70)
print(f"Expected Return: {ret_sharpe*100:.2f}%")
print(f"Volatility:      {vol_sharpe*100:.2f}%")
print(f"Sharpe Ratio:    {sharpe_ratio(w_sharpe):.3f}")
print("\nAllocation:", {f"Asset{i+1}": f"{w*100:.1f}%" for i, w in enumerate(w_sharpe) if w > 0.01})

print("\n" + "="*70)
print("MINIMUM VARIANCE PORTFOLIO")
print("="*70)
print(f"Expected Return: {ret_minvar*100:.2f}%")
print(f"Volatility:      {vol_minvar*100:.2f}%")
print(f"Sharpe Ratio:    {sharpe_ratio(w_minvar):.3f}")
print("\nAllocation:", {f"Asset{i+1}": f"{w*100:.1f}%" for i, w in enumerate(w_minvar) if w > 0.01})
print("="*70)
