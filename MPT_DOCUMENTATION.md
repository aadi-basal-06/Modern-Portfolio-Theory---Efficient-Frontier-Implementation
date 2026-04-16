# Modern Portfolio Theory - Efficient Frontier Implementation

## 📚 Overview

This project implements **Modern Portfolio Theory (MPT)** to optimize investment portfolios by constructing the **Efficient Frontier**—the set of optimal portfolios offering the highest expected return for a given level of risk.

---

## 🎯 Key Concepts

### 1. **Portfolio Return** (Linear Algebra: Dot Product)
The expected return of a portfolio is the weighted sum of individual asset returns:

```
R_p = w^T · μ

where:
  w = [w₁, w₂, ..., wₙ]ᵀ (portfolio weights)
  μ = [μ₁, μ₂, ..., μₙ]ᵀ (expected returns)
  R_p = portfolio return
```

**Implementation:**
```python
portfolio_return = np.dot(weights, mean_returns)
```

### 2. **Portfolio Volatility (Risk)** (Linear Algebra: Quadratic Form)
Portfolio risk is NOT simply the weighted sum of individual risks due to correlation effects:

```
σ_p = √(w^T · Σ · w)

where:
  Σ = covariance matrix (n × n)
  σ_p = portfolio volatility (standard deviation)
```

The covariance matrix captures correlations between assets. This is a **quadratic form**—the mathematical foundation of portfolio optimization.

**Implementation:**
```python
portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
```

### 3. **Sharpe Ratio** (Risk-Adjusted Performance Metric)
Measures how much excess return you get per unit of risk:

```
SR = (R_p - R_f) / σ_p

where:
  R_f = risk-free rate (e.g., 3% Treasury bills)
  Sharpe Ratio > 1.0 is considered good
  Sharpe Ratio > 2.0 is considered excellent
```

---

## 🧮 Mathematical Foundations

### Correlation & Covariance
Why covariance matters:
- **Diversification benefit**: If assets have low correlation, portfolio risk is reduced
- **Example**: 
  - Two perfectly correlated assets (ρ = 1): No diversification benefit
  - Two uncorrelated assets (ρ = 0): Maximum diversification benefit
  - Two negatively correlated assets (ρ = -1): Hedging effect

### Efficient Frontier Properties
1. **Concave hyperbola shape** in the (σ, R) plane
2. **No portfolio below the frontier** can achieve the same return with lower risk
3. **Capital Allocation Line (CAL)** connects risk-free rate to optimal portfolio
4. **Tangent Portfolio** (Max Sharpe Ratio) is where CAL touches the frontier

---

## 💻 Code Architecture

### `PortfolioOptimizer` Class

#### 1. **Initialization**
```python
optimizer = PortfolioOptimizer(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TESLA', 'META'],
    returns_data=mean_returns,      # numpy array of annual returns
    cov_matrix=cov_matrix,          # covariance matrix
    risk_free_rate=0.03
)
```

#### 2. **Portfolio Performance Calculation**
```python
def portfolio_performance(self, weights):
    # Linear algebra: w^T · μ
    portfolio_return = np.dot(weights, self.mean_returns)
    
    # Quadratic form: √(w^T · Σ · w)
    portfolio_volatility = np.sqrt(
        np.dot(weights.T, np.dot(self.cov_matrix, weights))
    )
    return portfolio_return, portfolio_volatility
```

#### 3. **Optimization Algorithms**

**Maximum Sharpe Ratio Portfolio:**
```python
minimize(negative_sharpe_ratio, 
         constraints=[sum(weights) = 1],
         bounds=[0 ≤ wᵢ ≤ 1])
```

**Minimum Variance Portfolio:**
```python
minimize(portfolio_volatility,
         constraints=[sum(weights) = 1],
         bounds=[0 ≤ wᵢ ≤ 1])
```

#### 4. **Efficient Frontier Generation**
For each target return, find minimum variance portfolio:
```
minimize: σ_p = √(w^T · Σ · w)
subject to: 
    ∑wᵢ = 1
    w^T · μ = R_target
    0 ≤ wᵢ ≤ 1
```

---

## 📊 Results Interpretation

### Output Metrics

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Expected Return** | w^T · μ | Annual expected profit (%) |
| **Volatility** | √(w^T · Σ · w) | Risk (standard deviation %) |
| **Sharpe Ratio** | (R - Rf) / σ | Risk-adjusted return (higher = better) |
| **Return/Risk Ratio** | R / σ | Absolute return per unit risk |

### Example Output

```
📋 MAXIMUM SHARPE RATIO PORTFOLIO
=========================================
Expected Annual Return:     19.43%
Annual Volatility (Risk):   24.96%
Sharpe Ratio:               0.658

Asset Allocation:
  NVDA:  40.37%  ← Highest weight (highest return/risk)
  MSFT:  25.20%  ← Second highest
  TESLA: 18.31%  ← Moderate weight
  AAPL:  12.55%
  GOOGL:  2.11%  ← Minimal weight
  META:   1.46%  ← Minimal weight
```

**Key Insight**: The optimizer allocates more weight to NVDA (high return, moderate risk) and less to META (low return).

---

## 🚀 Usage Guide

### Option 1: Real Data (Requires Network)
```python
from portfolio_optimization import PortfolioOptimizer
import yfinance as yf

# Fetch real data
tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TESLA', 'META']
optimizer = PortfolioOptimizer(
    tickers=tickers,
    start_date='2020-01-01',
    end_date='2024-01-01',
    risk_free_rate=0.03
)

# Generate and plot
max_sharpe_w, _, _, min_var_w = optimizer.plot_efficient_frontier()
```

### Option 2: Synthetic Data (Offline - No Network Required)
```python
from portfolio_optimization_v2 import PortfolioOptimizer, generate_synthetic_portfolio_data

# Generate synthetic data
mean_returns, cov_matrix = generate_synthetic_portfolio_data(num_assets=6)

optimizer = PortfolioOptimizer(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TESLA', 'META'],
    returns_data=mean_returns,
    cov_matrix=cov_matrix,
    risk_free_rate=0.03
)

# Optimize
max_sharpe_w, _, _, min_var_w = optimizer.plot_efficient_frontier(random_portfolios_num=5000)
```

---

## 📈 Linear Algebra Deep Dive

### Covariance Matrix (Σ)
```
     AAPL  MSFT GOOGL NVDA TESLA META
AAPL  0.0625  ...   ...   ...   ...  ...
MSFT   ...    0.0784 ...   ...   ...  ...
GOOGL  ...    ...   0.0484 ...   ...  ...
NVDA   ...    ...    ...  0.1024 ...  ...
TESLA  ...    ...    ...   ...  0.1225 ...
META   ...    ...    ...   ...   ...  0.04
```

**Why it matters:**
- **Diagonal** (Σᵢᵢ): Individual asset variance
- **Off-diagonal** (Σᵢⱼ): Covariance between assets
- **Symmetric**: Σᵢⱼ = Σⱼᵢ
- Determines how portfolio volatility scales with weights

### Quadratic Form: w^T · Σ · w
```
Step 1: Σ · w = [σ₁₁w₁ + σ₁₂w₂ + ..., σ₂₁w₁ + σ₂₂w₂ + ..., ...]ᵀ
Step 2: w^T · (Σ · w) = Σᵢⱼ Σ σᵢⱼ wᵢ wⱼ
Step 3: σ_p = √(w^T · Σ · w)
```

This quadratic form is why:
- Diversification works (cross-terms can be negative if assets are negatively correlated)
- A portfolio can have lower risk than its individual assets
- Doubling all weights quadruples the variance

---

## 🎓 Code Walkthrough

### Step 1: Load Data
```python
mean_returns = np.array([0.15, 0.18, 0.14, 0.22, 0.20, 0.12])  # Annual returns
cov_matrix = ...  # 6×6 matrix of covariances
```

### Step 2: Generate Random Portfolios (Visualization)
```python
for i in range(5000):
    weights = np.random.dirichlet(np.ones(6))  # Random allocation
    ret, vol = portfolio_performance(weights)
    sharpe = (ret - 0.03) / vol
    # Store for plotting
```

### Step 3: Optimize for Maximum Sharpe Ratio
```python
# Starting from equal weights
weights_0 = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6]

# Minimize: -(R_p - R_f) / σ_p
# Subject to: Σwᵢ = 1, 0 ≤ wᵢ ≤ 1
result = minimize(negative_sharpe, weights_0, method='SLSQP', ...)

# Optimal weights
weights_optimal = [0.1255, 0.2520, 0.0211, 0.4037, 0.1831, 0.0146]
```

### Step 4: Calculate Efficient Frontier
```python
# For each target return level
for target_ret in [0.12, 0.13, ..., 0.22]:
    # Find minimum volatility portfolio achieving that return
    weights_ef = minimize(
        portfolio_volatility,
        constraints=[Σwᵢ = 1, w^T·μ = target_ret],
        ...
    )
    efficient_vols.append(weights_ef.fun)
```

### Step 5: Visualize
```python
plt.scatter(random_vols, random_rets, c=random_sharpes)  # Random portfolios
plt.plot(ef_vols, ef_rets, 'r-', linewidth=3)  # Efficient frontier
plt.scatter(sharpe_vol, sharpe_ret, marker='*')  # Max Sharpe
```

---

## 📊 Visualization Explained

### Left Plot: Efficient Frontier
- **Purple/Yellow cloud**: 5,000 random portfolios (colored by Sharpe ratio)
- **Red curve**: The Efficient Frontier (optimal portfolios)
- **Gold star**: Maximum Sharpe Ratio portfolio (best risk-adjusted return)
- **Blue square**: Minimum Variance portfolio (lowest risk)
- **Green circle**: Risk-free asset (0% volatility, ~3% return)
- **Green dashed line**: Capital Allocation Line (optimal borrowing/lending)

### Right Plot: Portfolio Allocation
- **Horizontal bars**: Weight allocation for Max Sharpe Ratio portfolio
- **Colors**: Different assets
- **Percentages**: Exact allocation percentages

---

## ⚙️ Optimization Parameters

### Constraints
1. **Budget constraint**: Σwᵢ = 1 (all money must be allocated)
2. **No short-selling**: wᵢ ≥ 0 (can't borrow stocks to sell)
3. **No leverage limit**: wᵢ ≤ 1 (can't use margin beyond 100%)

### Optimization Method: SLSQP
- **Sequential Least Squares Programming**
- Handles non-linear objectives with non-linear constraints
- Convergence tolerance: 1e-9

---

## 🔢 Performance Metrics

### Example Results (6-Asset Portfolio)

| Portfolio | Return | Risk | Sharpe | Allocation |
|-----------|--------|------|--------|-----------|
| **Max Sharpe** | 19.43% | 24.96% | 0.658 | 40% NVDA, 25% MSFT, 18% TESLA, ... |
| **Min Variance** | 13.07% | 18.96% | 0.531 | 59% META, 27% GOOGL, 11% AAPL, ... |
| **Equally Weighted** | 16.83% | 26.42% | 0.533 | 16.67% each |

**Key Insights:**
- Max Sharpe portfolio: 625 bps higher return with only 100 bps more risk
- Min Variance portfolio: Heavily concentrated in low-volatility stocks
- Optimization beats naive equal weighting

---

## 🛠️ Advanced Extensions

### 1. Include Transaction Costs
```python
constraints = [Σwᵢ = 1, transaction_cost(w_new - w_old)]
```

### 2. Add Constraints
```python
# Minimum allocation: each stock ≥ 5%
bounds = tuple((0.05, 1) for _ in range(n))

# Maximum allocation: each stock ≤ 30%
bounds = tuple((0, 0.30) for _ in range(n))

# Sector constraints
constraints = [..., sector_constraint]
```

### 3. Black-Litterman Model
Incorporate analyst views with market equilibrium:
```python
prior_returns = market_implied_returns
posterior_returns = black_litterman(prior_returns, views)
```

### 4. Robust Optimization
Handle estimation uncertainty:
```python
# Worst-case optimization
minimize: max_σ ∈ uncertainty_set (w^T · Σ · w)
```

---

## 📚 References

1. **Markowitz, H. (1952)** - "Portfolio Selection" *The Journal of Finance*
2. **Sharpe, W. (1966)** - "Mutual Fund Performance" *The Journal of Business*
3. **Boyd, S. et al. (2006)** - "Convex Optimization" (chapters 4-5)

---

## ✅ Checklist for Success

- ✓ Portfolio returns calculated using linear algebra (dot product)
- ✓ Portfolio volatility using quadratic form (w^T · Σ · w)
- ✓ Efficient frontier computed via constrained optimization
- ✓ Maximum Sharpe Ratio portfolio identified
- ✓ Minimum Variance portfolio identified
- ✓ Visualization shows hyperbolic frontier curve
- ✓ Capital Allocation Line plotted
- ✓ Asset allocation pie/bar charts shown
- ✓ Performance metrics calculated (return, risk, Sharpe)

---

## 🚀 Next Steps

1. **Get Real Data**: Replace synthetic data with yfinance data
2. **Rebalance Strategy**: Update portfolio quarterly with new data
3. **Backtest**: Test strategy on historical data (walk-forward analysis)
4. **Add Constraints**: Implement sector or position limits
5. **Risk Management**: Add drawdown limits, VaR calculations

---

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| Optimization doesn't converge | Increase `maxiter`, relax tolerance |
| Frontier looks jagged | Increase number of target returns (num_portfolios) |
| All weights in one stock | Add maximum allocation constraints |
| Negative correlation not captured | Verify covariance matrix computation |

---

**Created**: 2024
**Version**: 2.0 (Synthetic Data Edition)
**Language**: Python 3.8+
**Dependencies**: NumPy, Pandas, SciPy, Matplotlib
