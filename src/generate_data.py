import pandas as pd
import numpy as np

def generate_synthetic_portfolio(num_assets=50):
    """
    Generates a synthetic portfolio of wholesale banking assets.
    """
    np.random.seed(42)
    asset_types = ['Corporate Loan', 'Sovereign Bond', 'MBS', 'Equity Derivative']
    
    data = {
        'Asset_ID': [f'AST_{i:04d}' for i in range(num_assets)],
        'Asset_Type': np.random.choice(asset_types, num_assets),
        'Exposure_USD': np.random.uniform(100000, 5000000, num_assets).round(2),
        'Risk_Weight': np.random.uniform(0.1, 1.5, num_assets).round(2),
    }
    
    df = pd.DataFrame(data)
    # Calculate initial Risk Weighted Assets (RWA)
    df['Initial_RWA'] = df['Exposure_USD'] * df['Risk_Weight']
    return df

if __name__ == "__main__":
    portfolio = generate_synthetic_portfolio()
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    portfolio.to_csv(os.path.join(data_dir, 'portfolio.csv'), index=False)
    print(f"Synthetic portfolio generated at {os.path.join(data_dir, 'portfolio.csv')}")
