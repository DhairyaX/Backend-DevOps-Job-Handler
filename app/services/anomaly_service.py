import pandas as pd

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies anomaly detection rules to the cleaned transactions dataframe.
    Returns the dataframe with `is_anomaly` and `anomaly_reason` columns updated.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Initialize columns
    df['is_anomaly'] = False
    # Using a temporary column to collect multiple reasons
    df['anomaly_reason_list'] = [[] for _ in range(len(df))]
    
    # Rule 1: Amount exceeds 3x account median
    if 'account_id' in df.columns and 'amount' in df.columns:
        # Calculate the median amount for each account_id
        medians = df.groupby('account_id')['amount'].transform('median')
        # Flag rows where amount is strictly greater than 3 * median
        mask1 = df['amount'] > (3 * medians)
        
        df.loc[mask1, 'is_anomaly'] = True
        for idx in df[mask1].index:
            df.at[idx, 'anomaly_reason_list'].append("Amount exceeds 3x account median")
            
    # Rule 2: Domestic merchant with USD transaction
    if 'merchant' in df.columns and 'currency' in df.columns:
        # Identify domestic merchants (Swiggy, Ola, IRCTC) and check for USD
        domestic_merchants = '^(Swiggy|Ola|IRCTC)$'
        mask2 = (
            df['merchant'].str.contains(domestic_merchants, case=False, regex=True, na=False) & 
            (df['currency'].str.upper() == 'USD')
        )
        
        df.loc[mask2, 'is_anomaly'] = True
        for idx in df[mask2].index:
            df.at[idx, 'anomaly_reason_list'].append("Domestic merchant with USD transaction")
            
    # Combine the reasons into a single string separated by " | "
    df['anomaly_reason'] = df['anomaly_reason_list'].apply(
        lambda x: " | ".join(x) if x else None
    )
    
    # Drop the temporary list column
    df = df.drop(columns=['anomaly_reason_list'])
    
    return df
