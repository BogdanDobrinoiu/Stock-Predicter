import joblib
import pandas as pd
import re
import os
import datetime as dt

with open('log.txt', 'a') as f:
    f.write(f'\n{dt.datetime.now()} -----------------------------------predict_companii.py-------------------------------------\n')

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

    last_run = get_last_run_number()

    filename = f'tests/bvb_merged_table_{last_run}.csv'
    df_predictie = pd.read_csv(filename)
    
    f.write('Transforming data into readable data for model\n')
    df_predictie.rename(columns={'Pret (RON)': 'Pret', 'Var. (%)': 'Var_Procent'}, inplace=True)
    df_predictie['Pret'] = pd.to_numeric(df_predictie['Pret'].astype(str).str.replace(',', '.'), errors='coerce')
    df_predictie['Var_Procent'] = pd.to_numeric(df_predictie['Var_Procent'].astype(str).str.replace(',', '.'), errors='coerce')
    df_predictie.dropna(subset=['Simbol', 'Pret', 'Var_Procent'], inplace=True)

    df_predictie['Pret_ieri'] = df_predictie['Pret']
    df_predictie['Var_procent_ieri'] = df_predictie['Var_Procent']
    
    f.write('Separatign features\n')
    FEATURES = ['Pret_ieri', 'Var_procent_ieri']
    X_final_pentru_predictie = df_predictie[FEATURES]

    f.write('Loading model\n')
    final_model = joblib.load('model_companii.joblib')

    f.write('Making predictions\n')
    predictions = final_model.predict(X_final_pentru_predictie)
    probabilities = final_model.predict_proba(X_final_pentru_predictie)

    f.write('Determining results\n')
    df_predictie['Predictie_ziua_urmatoare'] = ['Crește' if p == 1 else 'Scade/Stagnează' for p in predictions]
    df_predictie['Probabilitate_Creste'] = [f"{p[1]*100:.1f}%" for p in probabilities]

    columns_to_save = ['Simbol', 'Societate', 'Pret', 'Categorie', 'Predictie_ziua_urmatoare',
                    'Probabilitate_Creste']
    rezultat_final = df_predictie[columns_to_save]

    nume_fisier_temporar = "predictii_bvb_temporar.csv"
    rezultat_final.to_csv(nume_fisier_temporar, index=False)

    categories = rezultat_final['Categorie'].unique()

    f.write('Saving results into files\n')
    for category_name in categories:
        df_category = rezultat_final[rezultat_final['Categorie'] == category_name]
        clean_name = str(category_name).replace(' ', '_').replace(',', '').replace('&', 'si')
        file_name_category = f"predictii_{clean_name}.csv"
        df_category.to_csv(file_name_category, index=False)
    
    os.remove(nume_fisier_temporar)