import pandas as pd
import re
import os

def transform(run_number):
    df_initial = pd.read_csv(f"tests/bvb_merged_table_{run_number}.csv")

    coloane_necesare = ['Simbol', 'Pret (RON)', 'Var. (%)', 'Categorie']
    df = df_initial[coloane_necesare].copy()

    df.rename(columns={'Pret (RON)': 'Pret', 'Var. (%)': 'Var_Procent'}, inplace=True)

    df['Pret'] = pd.to_numeric(df['Pret'].astype(str).str.replace(',', '.'), errors='coerce')
    df['Var_Procent'] = pd.to_numeric(df['Var_Procent'].astype(str).str.replace(',', '.'), errors='coerce')

    df.dropna(subset=['Simbol', 'Pret', 'Var_Procent', 'Categorie'], inplace=True)

    df_indexed = df.set_index(['Categorie', 'Simbol'])

    df_wide = df_indexed.unstack()

    new_columns = [f"{simbol}_{metric}" for metric, simbol in df_wide.columns]
    df_wide.columns = new_columns

    simboluri_unice = df['Simbol'].unique()
    simboluri_unice.sort()

    coloane_ordonate = []
    for simbol in simboluri_unice:
        if f"{simbol}_Pret" in df_wide.columns:
            coloane_ordonate.append(f"{simbol}_Pret")
        if f"{simbol}_Var_Procent" in df_wide.columns:
            coloane_ordonate.append(f"{simbol}_Var_Procent")

    df_final = df_wide[coloane_ordonate]

    df_final.reset_index(inplace=True)

    df_final.to_csv(f"testsV2/bvb_categorii_wide_{run_number}.csv", index=False)

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
transform(run_number)

