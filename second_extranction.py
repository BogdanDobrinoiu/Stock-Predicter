from playwright.sync_api import sync_playwright
import pandas as pd
from io import StringIO

all_dataframes1 = []

input_file = "bvb_shares_all_pages_final.csv"
df = pd.read_csv(input_file)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
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
            print(f"Extracted {len(current_page_table)} rows from page {company_cnt}.")
        except IndexError:
            print("No table found. Next.")
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
    print("No data foound.")

df1 = pd.read_csv("bvb_more_data.csv")
df2 = pd.read_csv("bvb_shares_all_pages_final.csv")

merged_df = pd.merge(df2, df1, on="Simbol")

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

merged_df.to_csv("tests/bvb_merged_table.csv")



