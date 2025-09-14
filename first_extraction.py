from playwright.sync_api import sync_playwright
import pandas as pd
from io import StringIO
import os

# extract table 
all_dataframes = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.bvb.ro/FinancialInstruments/Markets/Shares", timeout=60000)

    page.wait_for_selector("table", timeout=15000)
    print("First page loaded.")

    page_count = 1
    while True:
        print(f"--- Procesing page {page_count} ---")

        page.wait_for_timeout(1000) 

        html = page.content()
        try:
            current_page_table = pd.read_html(StringIO(html))[0] 
            all_dataframes.append(current_page_table)
            print(f"Extracted {len(current_page_table)} rows from page {page_count}.")
        except IndexError:
            print("No table found. Next.")
            break

        next_button_selector = "#gv_next"
        next_button = page.locator(next_button_selector)

        if "disabled" in next_button.get_attribute("class"):
            print("\nLast page. End.")
            break
        else:
            print("Next page...")
            next_button.click()
            
            page.wait_for_load_state('networkidle', timeout=30000)
            page_count += 1
            
    browser.close()

if all_dataframes:
    final_table = pd.concat(all_dataframes, ignore_index=True)

    try:
        final_table.to_csv("bvb_shares_all_pages.csv", index=False, encoding='utf-8-sig')
        print("\nTabel saved to 'bvb_shares_all_pages.csv'")
    except Exception as e:
        print(f"\nError when saving to CSV: {e}")

else:
    print("No data found.")

#delete ISIN, save only symbol
df = pd.read_csv("bvb_shares_all_pages.csv")
df["Simbol / ISIN"] = df["Simbol / ISIN"].str[:-12]

df.rename(columns={"Simbol / ISIN" : "Simbol"}, inplace=True)

df.to_csv("bvb_shares_all_pages_final.csv", index=False)
print("Modified and saved changes.")

os.remove("bvb_shares_all_pages.csv")

