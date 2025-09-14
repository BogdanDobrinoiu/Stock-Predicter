import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import glob
import joblib
import datetime as dt

with open('log.txt', 'a') as f:
    f.write(f'\n{dt.datetime.now()} -------------------------------------------ml_categoriiV2.py---------------------------------------\n')

    all_files = sorted(glob.glob('testsV2/bvb_categorii_wide_*.csv'))
    PROFITABILITY_THRESHOLD = 0.5
    CATEGORII = [
        "Energie si Utilitati",
        "Sector Financiar si Investitii",
        "Industrie, Constructii si Materiale",
        "Servicii, Tehnologie si Bunuri de Consum"
    ]

    for categorie in CATEGORII:
        f.write(f'Training for {categorie} category\n')
        all_daily_data = []

        f.write('Reading files and creating necessary columns for training\n')
        for filename in all_files:
            df_day = pd.read_csv(filename)
            pret_cols = [col for col in df_day.columns if '_Pret' in col]
            suma_preturilor = df_day[pret_cols].sum().sum()

            df_categorie = df_day[df_day['Categorie'] == categorie]
            series = df_categorie.isna().sum()
            series = series[series == 0]
            columns = series.index
            df_categorie = df_categorie[columns]

            profitabil_azi = 0
            if not df_categorie.empty:
                var_procent_cols = [col for col in df_categorie.columns if '_Var_Procent' in col]
                variatii = df_categorie[var_procent_cols].values[0]
                variatii_valide = variatii[~np.isnan(variatii)]
                if len(variatii_valide) > 0:
                    profitabil_azi = 1 if np.mean(variatii_valide) > PROFITABILITY_THRESHOLD else 0
            
            df_categorie.loc[:,'profitabil_azi'] = profitabil_azi
            df_categorie.loc[:,'suma_preturi_azi'] = suma_preturilor
            all_daily_data.append(df_categorie)

        f.write('Saving new dataframe and cleaning it\n')
        daily_data = pd.concat(all_daily_data, ignore_index=True)

        model_df = pd.DataFrame(daily_data)
        model_df['suma_preturi_ieri'] = model_df['suma_preturi_azi'].shift(1)
        model_df['piata_a_crescut'] = (model_df['suma_preturi_azi'] > model_df['suma_preturi_ieri']).astype(int)
        model_df['target_profitabil_maine'] = model_df['profitabil_azi'].shift(-1)

        final_df = model_df.dropna().copy()
        final_df['target_profitabil_maine'] = final_df['target_profitabil_maine'].astype(int)

        f.write('Separating features from targets\n')
        X = final_df.drop(columns=['Categorie', 'target_profitabil_maine'])
        y = final_df['target_profitabil_maine']

        if y.nunique() < 2:
            print("\nWARNING: toate datele au acelasi rezultat")
            known_class = y.iloc[0]
            result_text = "PROFITABIL" if known_class == 1 else "NEPROFITABIL"
            print(f"Pentru ca toate zilele din istoric au fost '{result_text}', predicția este tot '{result_text}'")
        else:
            f.write('Training the model\n')
            final_model = LogisticRegression(max_iter=100000)
            final_model.fit(X, y)

            clean_name = str(categorie).replace(' ', '_').replace(',', '').replace('&', 'si')
            joblib.dump(final_model, f'model_{clean_name}.joblib')

            data_for_prediction = pd.DataFrame(X)
            prediction_for_tomorrow = final_model.predict(data_for_prediction)
            prediction_proba = final_model.predict_proba(data_for_prediction)
