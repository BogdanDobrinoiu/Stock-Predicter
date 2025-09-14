import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os
import re
import joblib
import datetime as dt

with open('log.txt', 'a') as f:
    f.write(f'\n{dt.datetime.now()} --------------------------------------------------ml_tmr.py-----------------------------------------\n')

    def get_last_run_number(folder="tests"):
        max_run = -1
        pattern = re.compile(r"bvb_merged_table_(\d+)\.csv")

        for filename in os.listdir(folder):
            match = pattern.match(filename)
            if match:
                run_num = int(match.group(1))
                if run_num > max_run:
                    max_run = run_num

        return max_run if max_run >= 0 else None

    run_number = get_last_run_number()
    run_number += 1

    file_names = [f'tests/bvb_merged_table_{i}.csv' for i in range(run_number)]

    df_list = []
    for i, filename in enumerate(file_names):
        df_day = pd.read_csv(filename)
        df_day['zi_colectare'] = i
        df_list.append(df_day)


    full_df = pd.concat(df_list, ignore_index=True)

    f.write('Creating necessary columns for training')
    full_df.rename(columns={'Pret (RON)': 'Pret', 'Var. (%)': 'Var_Procent'}, inplace=True)
    full_df['Pret'] = pd.to_numeric(full_df['Pret'].astype(str).str.replace(',', '.'), errors='coerce')
    full_df['Var_Procent'] = pd.to_numeric(full_df['Var_Procent'].astype(str).str.replace(',', '.'), errors='coerce')
    full_df.dropna(subset=['Simbol', 'Pret', 'Var_Procent'], inplace=True)

    full_df.sort_values(by=['Simbol', 'zi_colectare'], inplace=True)

    df_processed = full_df.copy()
    grouped = df_processed.groupby('Simbol')

    df_processed['Pret_ieri'] = df_processed.groupby('Simbol')['Pret'].shift(1)
    df_processed['Var_procent_ieri'] = df_processed.groupby('Simbol')['Var_Procent'].shift(1)
    next_price = df_processed.groupby('Simbol')['Pret'].shift(-1)
    df_processed['Target_1_zi'] = (next_price > df_processed['Pret']).astype(int)

    df_processed.dropna(inplace=True)

    f.write('Separatign features from tragets\n')
    FEATURES = ['Pret_ieri', 'Var_procent_ieri']
    TARGET = 'Target_1_zi'

    X = df_processed[FEATURES]
    y = df_processed[TARGET]

    f.write('Training model\n')
    model = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced')
    model.fit(X, y)
        
    prediction_data = full_df.drop_duplicates(subset='Simbol', keep='last').copy()
    prediction_data['Pret_ieri'] = prediction_data['Pret']
    prediction_data['Var_procent_ieri'] = prediction_data['Var_Procent']

    X_pred = prediction_data[FEATURES]
        
    predictions = model.predict(X_pred)
    probabilities = model.predict_proba(X_pred)

    f.write('Saving model\n')
    joblib.dump(model, 'model_companii.joblib')
