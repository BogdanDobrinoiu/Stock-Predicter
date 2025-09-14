from playwright.sync_api import sync_playwright, ViewportSize
import pandas as pd
from io import StringIO
import os
import re
import datetime as dt

with open('log.txt', 'a') as f:
    f.write(f'\n{dt.datetime.now()} ------------------------------------data_selector.py----------------------------------------\n')
    df_categorize = pd.read_csv("categorize.csv")

    def main(run_number):
        all_dataframes = []

        f.write('Scrapping for tables\n')
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport= ViewportSize(width= 1280, height= 800),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
            )
            page = context.new_page()
            page.goto("https://www.bvb.ro/FinancialInstruments/Markets/Shares", timeout=60000)

            page.wait_for_selector("table", timeout=15000)

            page_count = 1

            while True:
                page.wait_for_timeout(1000) 

                html = page.content()
                try:
                    current_page_table = pd.read_html(StringIO(html))[0] 
                    all_dataframes.append(current_page_table)
                except IndexError:
                    f.write("No table found. Next.\n")
                    break

                next_button_selector = "#gv_next"
                next_button = page.locator(next_button_selector)

                if "disabled" in next_button.get_attribute("class"):
                    break
                else:
                    next_button.click() 
                    
                    page.wait_for_load_state('networkidle', timeout=30000)
                    page_count += 1
                    
            browser.close()

        if all_dataframes:
            final_table = pd.concat(all_dataframes, ignore_index=True)

            try:
                final_table.to_csv("bvb_shares_all_pages.csv", index=False, encoding='utf-8-sig')
            except Exception as e:
                f.write(f"\nError when saving to CSV: {e}\n")

        else:
            f.write("No data found.\n")

        df = pd.read_csv("bvb_shares_all_pages.csv")
        df["Simbol / ISIN"] = df["Simbol / ISIN"].str[:-12]

        df.rename(columns={"Simbol / ISIN" : "Simbol"}, inplace=True)

        df.to_csv("bvb_shares_all_pages_final.csv", index=False)

        os.remove("bvb_shares_all_pages.csv")

        all_dataframes1 = []

        input_file = "bvb_shares_all_pages_final.csv"
        df = pd.read_csv(input_file)

        f.write('Extracting info about each company\n')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport= ViewportSize(width= 1280, height= 800),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
            )
            page = context.new_page()
            company_cnt = 0

            for i in df["Simbol"]:
                url1 = "https://www.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s=" + i
                page.goto(url1)

                price_table = page.locator("#ctl00_body_ctl02_PricesControl_dvCPrices")

                html = price_table.inner_html()

                try:
                    html = "<table>" + html + "</table>"
                    current_page_table = pd.read_html(StringIO(html))[0] 
                    all_dataframes1.append(current_page_table)
                except IndexError:
                    f.write("No table found. Next.\n")
                    break

                company_cnt += 1

            browser.close()

        if all_dataframes1:
            rows = []

            for idx, partial_df in enumerate(all_dataframes1):
                symbol = df["Simbol"].iloc[idx]

                partial_df = partial_df.dropna().reset_index(drop=True)

                partial_df.columns = ["Field", "Value"]
                data = partial_df.set_index("Field")["Value"].to_dict()
                data["Simbol"] = symbol
                rows.append(data)

                final_df = pd.DataFrame(rows)

                cols = ["Simbol"] + [col for col in final_df.columns if col != "Simbol"]
                final_df = final_df[cols]

                final_df.to_csv("bvb_more_data.csv", index=False)

        else:
            f.write("No data foound.\n")

        df1 = pd.read_csv("bvb_more_data.csv")
        df2 = pd.read_csv("bvb_shares_all_pages_final.csv")

        merged_df = pd.merge(df2, df1, on="Simbol")

        f.write('Cleaning data\n')
        merged_df["Pret (RON)"] = merged_df["Pret (RON)"] / 10000
        merged_df["Pret (RON)"] = merged_df["Pret (RON)"].map(lambda x: f"{x: .4f}")

        merged_df["Var. (%)"] = merged_df["Var. (%)"] / 100
        merged_df["Var. (%)"] = merged_df["Var. (%)"].map(lambda x: f"{x: .2f}")

        merged_df["Pret referinta"] = merged_df["Pret referinta"] / 10000
        merged_df["Pret referinta"] = merged_df["Pret referinta"].map(lambda x: f"{x: .4f}")

        merged_df["Ultimul pret"] = merged_df["Ultimul pret"] / 10000
        merged_df["Ultimul pret"] = merged_df["Ultimul pret"].map(lambda x: f"{x: .4f}")

        merged_df["Pret maxim"] = merged_df["Pret maxim"] / 10000
        merged_df["Pret maxim"] = merged_df["Pret maxim"].map(lambda x: f"{x: .4f}")

        merged_df["Pret minim"] = merged_df["Pret minim"] / 10000
        merged_df["Pret minim"] = merged_df["Pret minim"].map(lambda x: f"{x: .4f}")

        merged_df["Pret mediu"] = merged_df["Pret mediu"] / 10000
        merged_df["Pret mediu"] = merged_df["Pret mediu"].map(lambda x: f"{x: .4f}")

        merged_df["Max. 52 saptamani"] = merged_df["Max. 52 saptamani"] / 10000
        merged_df["Max. 52 saptamani"] = merged_df["Max. 52 saptamani"].map(lambda x: f"{x: .4f}")

        merged_df["Min. 52 saptamani"] = merged_df["Min. 52 saptamani"] / 10000
        merged_df["Min. 52 saptamani"] = merged_df["Min. 52 saptamani"].map(lambda x: f"{x: .4f}")

        merged_df["Var"] = merged_df["Var"] / 10000
        merged_df["Var"] = merged_df["Var"].map(lambda x: f"{x: .4f}")

        merged_df["Pret deschidere"] = merged_df["Pret deschidere"] / 10000
        merged_df["Pret deschidere"] = merged_df["Pret deschidere"].map(lambda x: f"{x: .4f}")

        final_merged_df = pd.merge(merged_df, df_categorize, on='Simbol', how='left')

        output_path = f"tests/bvb_merged_table_{run_number}.csv"
        final_merged_df.to_csv(output_path)

        f.write('Deleting temporary files')
        os.remove("bvb_more_data.csv")
        os.remove("bvb_shares_all_pages_final.csv")

        all_dataframes.clear()
        all_dataframes1.clear()

    def transform(run_number):
        f.write('Tranforming data into readable data for category model\n')
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

    last_run = get_last_run_number()
    last_run += 1
    main(last_run)
    transform(last_run)
