import pandas as pd
import datetime
import os

DATA_DIR = 'data'

def init_data():
    """Menginisialisasi atau memuat DataFrames dari file CSV."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
       
    def load_or_create(filename, columns, dtypes=None):
        path = os.path.join(DATA_DIR, filename)
        try:
            df = pd.read_csv(path)
            if dtypes:
                for col, dtype in dtypes.items():
                    if dtype == 'int':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                    elif dtype == 'datetime':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
        except FileNotFoundError:
            df = pd.DataFrame(columns=columns)
            if dtypes:
                for col, dtype in dtypes.items():
                    if dtype == 'int':
                        df[col] = df[col].astype(int) if col in df.columns else []
                    elif dtype == 'datetime':
                        df[col] = pd.to_datetime(df[col]) if col in df.columns else []
        return df