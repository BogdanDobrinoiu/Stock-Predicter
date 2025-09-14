import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import glob
from contextlib import redirect_stdout

with open("predictii_toti.txt", "w", encoding="utf-8") as f:
    with redirect_stdout(f):
        all_files = sorted(glob.glob('testsV2/bvb_categorii_wide_*.csv'))
        PROFITABILITY_THRESHOLD = 0.5
        CATEGORII = [
            "Energie si Utilitati",
            "Sector Financiar si Investitii",
            "Industrie, Constructii si Materiale",
            "Servicii, Tehnologie si Bunuri de Consum"
        ]

        for categorie in CATEGORII:
            daily_data = []
            for filename in all_files:
                df_day = pd.read_csv(filename)

                pret_cols = [col for col in df_day.columns if '_Pret' in col]
                suma_preturilor = df_day[pret_cols].sum().sum()

                df_energie = df_day[df_day['Categorie'] == categorie]
                profitabil_azi = 0
                if not df_energie.empty:
                    var_procent_cols = [col for col in df_energie.columns if '_Var_Procent' in col]
                    variatii = df_energie[var_procent_cols].values[0]
                    variatii_valide = variatii[~np.isnan(variatii)]
                    if len(variatii_valide) > 0:
                        profitabil_azi = 1 if np.mean(variatii_valide) > PROFITABILITY_THRESHOLD else 0

                daily_data.append({
                    'suma_preturi_azi': suma_preturilor,
                    'profitabil_azi': profitabil_azi
                })

            model_df = pd.DataFrame(daily_data)
            model_df['suma_preturi_ieri'] = model_df['suma_preturi_azi'].shift(1)
            model_df['piata_a_crescut'] = (model_df['suma_preturi_azi'] > model_df['suma_preturi_ieri']).astype(int)
            model_df['target_profitabil_maine'] = model_df['profitabil_azi'].shift(-1)

            final_df = model_df.dropna().copy()
            final_df['target_profitabil_maine'] = final_df['target_profitabil_maine'].astype(int)

            X = final_df[['piata_a_crescut']]
            y = final_df['target_profitabil_maine']

            if y.nunique() < 2:
                print("\nWARNING: toate datele au acelasi rezultat")
                known_class = y.iloc[0]
                result_text = "PROFITABIL" if known_class == 1 else "NEPROFITABIL"
                print(f"Pentru ca toate zilele din istoric au fost '{result_text}', predicția este tot '{result_text}'")
            else:
                final_model = LogisticRegression()
                final_model.fit(X, y)

                piata_creste_azi = model_df.tail(1)['piata_a_crescut'].values[0]
                data_for_prediction = pd.DataFrame({'piata_a_crescut': [piata_creste_azi]})
                prediction_for_tomorrow = final_model.predict(data_for_prediction)[0]
                prediction_proba = final_model.predict_proba(data_for_prediction)

                result_text = "PROFITABIL" if prediction_for_tomorrow == 1 else "NEPROFITABIL"
                proba_index = 1 if prediction_for_tomorrow == 1 else 0
                print(f"{result_text},")
                print(f"{prediction_proba[0][proba_index]:.2f},")
