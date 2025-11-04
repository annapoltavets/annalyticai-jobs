import os
import pandas as pd


import hashlib


# Example DataFrame


# Generate unique hash key based on key columns
def generate_hash(x):
    return hashlib.md5(x.encode()).hexdigest()

def load_data(folder_path: str, subset: list = None) -> pd.DataFrame:
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
    dataframes = []
    for file in json_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_json(file_path, lines=True)
        df['file_name'] = file
        dataframes.append(df)

    df = pd.concat(dataframes, ignore_index=True)
    if subset != None:
        df = df.drop_duplicates(subset=subset, ignore_index=True)
    return df

def load_dir(folder_path: str, subdirs, subset: list = None) -> pd.DataFrame:
    parsed = []
    for dr in subdirs:
        if os.path.exists(f'{folder_path}/{dr}'):
            parsed_df = load_data(f'{folder_path}/{dr}', subset=subset)
            parsed.append(parsed_df)
    return pd.concat(parsed, ignore_index=True)


def load_csv(folder_path: str) -> pd.DataFrame:
    files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    dataframes = []
    for file in files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    df = pd.concat(dataframes, ignore_index=True)
    print(df.shape)
    return df