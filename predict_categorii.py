import pandas as pd
import numpy as np
import glob
import joblib
import re
import datetime as dt

with open('log.txt', 'a') as f:
    f.write(f'\n{dt.datetime.now()} ----------------------------------------predict_categorii.py-----------------------------\n')

    def get_clean_filename(name):
        return re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_').replace('&', 'si'))

    PROFITABILITY_THRESHOLD = 0.5
    CATEGORII = [
        "Energie si Utilitati",
        "Sector Financiar si Investitii",
        "Industrie, Constructii si Materiale",
        "Servicii, Tehnologie si Bunuri de Consum"
    ]

    all_files = sorted(glob.glob('testsV2/bvb_categorii_wide_*.csv'))

    fisier_azi = all_files[-1]
    fisier_ieri = all_files[-2]

    df_azi = pd.read_csv(fisier_azi)
    df_ieri = pd.read_csv(fisier_ieri)

    f.write('Creating necessary columns\n')
    pret_cols_azi = [col for col in df_azi.columns if '_Pret' in col]
    suma_preturi_azi = df_azi[pret_cols_azi].sum().sum()

    pret_cols_ieri = [col for col in df_ieri.columns if '_Pret' in col]
    suma_preturi_ieri = df_ieri[pret_cols_ieri].sum().sum()

    piata_a_crescut = 1 if suma_preturi_azi > suma_preturi_ieri else 0

    rezultate_predictii = []

    f.write('Entering predicting loop\n')
    for categorie in CATEGORII:
        f.write(f'Predicting for {categorie} category\n')
        df_categorie_azi = df_azi[df_azi['Categorie'] == categorie].copy()
        
        series = df_categorie_azi.isna().sum()
        series = series[series == 0]
        columns = series.index
        df_categorie_azi = df_categorie_azi[columns]
        
        profitabil_azi = 0
        if not df_categorie_azi.empty:
            var_procent_cols = [col for col in df_categorie_azi.columns if '_Var_Procent' in col]
            variatii = df_categorie_azi[var_procent_cols].values[0]
            variatii_valide = variatii[~np.isnan(variatii)]
            if len(variatii_valide) > 0:
                profitabil_azi = 1 if np.mean(variatii_valide) > PROFITABILITY_THRESHOLD else 0

        data_pentru_predictie = df_categorie_azi.drop(columns=['Categorie'], errors='ignore')
        data_pentru_predictie['profitabil_azi'] = profitabil_azi
        data_pentru_predictie['suma_preturi_azi'] = suma_preturi_azi
        data_pentru_predictie['suma_preturi_ieri'] = suma_preturi_ieri
        data_pentru_predictie['piata_a_crescut'] = piata_a_crescut
        
        model_filename = f"model_{get_clean_filename(categorie)}.joblib"
        f.write('Loading model\n')
        model = joblib.load(model_filename)

        X_final = data_pentru_predictie[model.feature_names_in_]
        
        predictie = model.predict(X_final)[0]
        probabilitati = model.predict_proba(X_final)[0]
        probabilitate_profit = probabilitati[list(model.classes_).index(1)]

        rezultat_text = "PROFITABILĂ" if predictie == 1 else "NEPROFITABILĂ"
        
        rezultate_predictii.append({
            'Categorie': categorie,
            'Predictie Maine': rezultat_text,
            'Probabilitate Profit': f"{probabilitate_profit*100:.1f}%"
        })

    df_rezultate = pd.DataFrame(rezultate_predictii)

    f.write('Saving output\n')
    nume_fisier_output = "predictii_categorii.csv"
    df_rezultate.to_csv(nume_fisier_output, index=False)
