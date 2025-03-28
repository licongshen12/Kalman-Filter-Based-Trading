# Kalman-Filter-Trading-Strategy

This repo implements a statistical arbitrage strategy between BTC-PERP and BTC 3M futures using a Kalman Filter for dynamic hedge ratio estimation.

## Structure
- `src/`: Core logic
- `scripts/`: Execution scripts for backtesting and live trading
- `data/`: Raw and processed data
- `notebooks/`: Exploratory work
- `reports/`: Output reports and plots

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Kalman-Filter-Based-Trading.git
cd Kalman-Filter-Based-Trading
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
```

### 3. Activate the environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.\.venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. (Optional) Register the environment as a Jupyter kernel
```bash
python -m ipykernel install --user --name kalman_venv --display-name "Python (kalmanvenv)"
```

### 6. Launch Jupyter Notebook
```bash
jupyter notebook
```

Open `notebooks/kalman_model_dev.ipynb` and select the `Python (kalmanvenv)` kernel from the top-right dropdown.

## Quick Start
```bash
pip install -r requirements.txt
python scripts/backtest.py
```

